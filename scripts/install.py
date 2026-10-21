#!/usr/bin/env python3
"""Install Dishi's runtime subset offline. Python 3.9+."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("dishi_package_rules", Path(__file__).with_name("package_rules.py"))
rules = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rules)
REQUIRED = rules.REQUIRED


def destination_for(target, destination=None):
    if destination:
        return Path(destination).expanduser().absolute()
    scope = ".agents" if target == "codex" else ".claude"
    legacy = Path.home() / ".codex" / "skills" / "dishi"
    if target == "codex" and legacy.exists():
        raise ValueError("Existing legacy install found. Use --destination to update that folder, or remove it before a new install. / 发现旧位置的帝师，请指定该目录更新，避免重复。")
    return Path.home() / scope / "skills" / "dishi"


def check_paths(source, destination):
    if not source.is_dir():
        raise ValueError("Source package directory is missing.")
    if destination.name != "dishi":
        raise ValueError("Destination must be a skill folder named 'dishi'. / 目标目录须名为 dishi。")
    if destination.is_symlink():
        raise ValueError("The destination skill itself cannot be a symbolic link. / 技能目标本身不能为符号链接。")
    source, resolved = source.resolve(), destination.resolve()
    if source == resolved or source in resolved.parents or resolved in source.parents:
        raise ValueError("Source and destination must not overlap. / 源目录与安装目录不能重叠。")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError("Source contains a symbolic link: " + path.relative_to(source).as_posix())


def skill_scan_root(destination):
    for parent in destination.parents:
        if parent.name == "skills":
            return parent
    return destination.parent


def backup_directory(destination, specified=None):
    destination = Path(destination).resolve()
    standard = {Path.home() / scope / "skills" / "dishi" for scope in (".agents", ".claude", ".codex")}
    if specified is not None:
        directory = Path(specified).expanduser().absolute().resolve()
    elif destination in {path.resolve() for path in standard}:
        directory = Path.home() / ".local" / "share" / "dishi" / "backups"
    else:
        scan_root = skill_scan_root(destination)
        outer = scan_root.parent
        if outer.name in {".agents", ".claude", ".codex"}:
            outer = outer.parent
        directory = outer / ".dishi-backups" / (scan_root.name + "-installs")
    directory = directory.resolve()
    scan_root = skill_scan_root(destination)
    if (directory == scan_root or scan_root in directory.parents
            or any(parent.name == "skills" for parent in (directory,) + tuple(directory.parents))):
        raise ValueError("Backup directory must be outside the skill scan directory.")
    return directory


def relative_error(error, roots):
    message = str(error)
    labels = {str(Path(root)): label for root, label in roots}
    for root, label in sorted(labels.items(), key=lambda row: -len(row[0])):
        message = message.replace(root + os.sep, label + "/").replace(root, label)
    return message


def run_json(payload, arguments, timeout, purpose):
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(payload / "knowledge/kb.py")] + arguments,
            capture_output=True, text=True, encoding="utf-8", timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise ValueError(purpose + " timed out after " + str(timeout) + " seconds.") from None
    if result.returncode:
        details = result.stderr.strip() or result.stdout.strip()
        try:
            failed = json.loads(result.stdout)
            book_errors = [str(book.get("id", "?")) + ": " + "; ".join(book.get("errors", []))
                           for book in failed.get("books", []) if not book.get("valid")]
            if book_errors:
                details = "; ".join(book_errors)
        except (ValueError, AttributeError, TypeError):
            pass
        raise ValueError(purpose + " failed: " + relative_error(details[-4000:], [(payload, ".")]))
    try:
        document = json.loads(result.stdout)
    except (ValueError, TypeError):
        raise ValueError(purpose + " returned invalid JSON.") from None
    if not isinstance(document, dict):
        raise ValueError(purpose + " returned an invalid result object.")
    return document


def install(source, destination, replace=False, dry_run=False, backup_dir=None):
    source, destination = Path(source), Path(destination)
    check_paths(source, destination)
    source, destination = source.resolve(), destination.resolve()
    if destination.exists() and not destination.is_dir():
        raise ValueError("Destination exists and is not a directory.")
    if destination.exists() and not replace:
        raise ValueError("Dishi already exists. Use --replace to back it up and update it. / 已有版本；用 --replace 备份后更新。")
    backups = backup_directory(destination, backup_dir)
    if backups == source or source in backups.parents or backups in source.parents:
        raise ValueError("Backup directory and source package must not overlap.")
    missing = [name for name in REQUIRED if not (source / name).is_file()]
    if missing:
        raise ValueError("Incomplete skill package / 技能包缺少文件: " + ", ".join(missing))
    report = {"destination": str(destination), "dry_run": dry_run, "backup": None}
    if dry_run:
        return report
    roots = [(source, "<source>"), (destination, "<destination>"),
             (destination.parent, "<skill-directory>"), (backups, "<backups>")]
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".dishi-install-", dir=str(destination.parent)) as stage:
            stage = Path(stage)
            roots.append((stage, "<staging>"))
            payload = stage / "dishi"
            payload.mkdir()
            for path, relative in rules.inventory(source):
                if rules.runtime_includes(relative):
                    target = payload / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    content = rules.public_bytes(relative, path.read_bytes())
                    rules.check_public_text(relative, content)
                    target.write_bytes(content)
            validated = run_json(payload, ["validate"], 180, "Copied knowledge base validation")
            if (validated.get("valid") is not True or not isinstance(validated.get("books"), list)
                    or not validated["books"]):
                raise ValueError("Copied knowledge base is not valid or returned no book results.")
            english = run_json(payload, ["explain-query", "trust and cooperation", "--json"], 30,
                               "Copied English query mapping")
            if not english.get("mapped_keywords"):
                raise ValueError("Copied English query mapping returned no keywords.")
            backup = None
            previous = stage / "previous"
            if destination.exists():
                if not replace:
                    raise ValueError("Dishi appeared during validation. Use --replace to update it.")
                if destination.is_symlink() or not destination.is_dir():
                    raise ValueError("Destination changed during validation; expected a regular skill directory.")
                backups.mkdir(parents=True, exist_ok=True)
                container = Path(tempfile.mkdtemp(prefix="dishi-", dir=str(backups)))
                backup = container / "dishi"
                # Copy before swapping, since the backup store may use another filesystem.
                try:
                    shutil.copytree(destination, backup, symlinks=True)
                except OSError:
                    shutil.rmtree(container)
                    raise
                os.replace(destination, previous)
            try:
                os.replace(payload, destination)
            except OSError:
                if previous.exists():
                    try:
                        os.replace(previous, destination)
                    except OSError as restore_error:
                        saved = "<backups>/" + backup.relative_to(backups).as_posix()
                        raise ValueError("Replacement and automatic restoration failed. "
                                         "The existing version is preserved at " + saved + ". "
                                         + str(restore_error)) from None
                raise
            report["backup"] = str(backup) if backup else None
            report["books"] = len(validated["books"])
        return report
    except (OSError, ValueError, UnicodeError) as error:
        raise ValueError(relative_error(error, roots)) from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("codex", "claude"), default="codex")
    parser.add_argument("--destination", help="Exact destination skill folder, ending in dishi")
    parser.add_argument("--replace", action="store_true", help="Back up an existing skill before replacement")
    parser.add_argument("--backup-dir", type=Path, help="Backup store outside the skill scan tree; existing backups are retained")
    parser.add_argument("--dry-run", action="store_true", help="Check paths and required files without modifying files")
    args = parser.parse_args(argv)
    try:
        destination = destination_for(args.target, args.destination)
        print(json.dumps(install(ROOT, destination, args.replace, args.dry_run, args.backup_dir), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print("Install failed / 安装失败: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
