#!/usr/bin/env python3
"""Build a filtered, checksummed public folder and ZIP without publishing."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("dishi_package_rules", Path(__file__).with_name("package_rules.py"))
rules = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rules)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def release_bytes(relative, data):
    return rules.public_bytes(relative, data)


def included_files(root):
    for path, relative in rules.inventory(root):
        if not rules.process_exclusion(relative):
            yield path, relative


def build(root, destination):
    root = Path(root).resolve()
    destination = Path(destination).absolute()
    if destination.is_symlink():
        raise ValueError("The release destination itself cannot be a symbolic link.")
    destination = destination.resolve()
    if root == destination or root in destination.parents or destination in root.parents:
        raise ValueError("Release input and output must not overlap.")
    required = rules.REQUIRED + ("scripts/install.py", "scripts/package_rules.py")
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise ValueError("Incomplete release input; missing: " + ", ".join(missing))
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("VERSION must contain a three-part numeric version.")
    archive = destination.parent / ("dishi-" + version + ".zip")
    if destination.exists() or archive.exists():
        raise ValueError("Release output already exists; select a fresh output directory.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    records, excluded, allowed_metadata = [], [], []
    with tempfile.TemporaryDirectory(prefix=".dishi-release-", dir=str(destination.parent)) as temp:
        tree = Path(temp) / "dishi"
        tree.mkdir()
        for path, relative in rules.inventory(root):
            before = path.read_bytes()
            reason = rules.process_exclusion(relative)
            if reason:
                excluded.append({"path": relative, "source_bytes": len(before),
                                 "source_sha256": digest(before), "reason": reason})
                continue
            after = release_bytes(relative, before)
            allowed_metadata.extend(rules.check_public_text(relative, after))
            if relative in rules.PROCESS_PATH_NOTES and rules.LOCAL_PROCESS_PATH.search(after.decode("utf-8")):
                raise ValueError("Unredacted process workspace path in " + relative)
            target = tree / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(after)
            record = {"path": relative, "bytes": len(after), "sha256": digest(after)}
            if before != after:
                record["source_sha256"] = digest(before)
                record["change"] = (
                    "Archived-local evidence entries and source-tree hash scope disclosed."
                    if relative == "docs/source-attribution.json" else
                    "Links to archived workflow records point to the public provenance summary. "
                    "Local process-workspace paths are replaced only in the declared process note."
                )
            records.append(record)
        manifest = {
            "schema_version": 2, "version": version,
            "scope": "Public files excluding this manifest; source evidence remains unchanged locally; no upload performed.",
            "files": records, "excluded_local_records": excluded,
            "exclusion_rules": [{"pattern": pattern, "reason": reason} for pattern, reason in rules.PROCESS_EXCLUSIONS],
            "public_summary": rules.SUMMARY_ANCHOR,
            "allowed_historical_metadata": allowed_metadata,
        }
        (tree / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        staged_zip = Path(temp) / "release.zip"
        with zipfile.ZipFile(staged_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            for path in sorted(tree.rglob("*")):
                if path.is_file():
                    info = zipfile.ZipInfo("dishi/" + path.relative_to(tree).as_posix(), (2026, 10, 20, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    output.writestr(info, path.read_bytes())
        os.replace(tree, destination)
        try:
            os.replace(staged_zip, archive)
        except OSError:
            shutil.rmtree(destination)
            raise
    return {"directory": str(destination), "archive": str(archive), "files": len(records) + 1,
            "zip_sha256": digest(archive.read_bytes()),
            "changed_files": [row["path"] for row in records if "change" in row],
            "excluded_records": len(excluded), "excluded_bytes": sum(row["source_bytes"] for row in excluded)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Fresh release folder, outside the source checkout")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(ROOT, args.output), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, UnicodeError) as error:
        message = str(error)
        for path, label in ((ROOT, "<source>"), (args.output.absolute(), "<output>"),
                            (args.output.absolute().resolve().parent, "<output-parent>")):
            message = message.replace(str(path), label)
        print("Release build failed / 打包失败: " + message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
