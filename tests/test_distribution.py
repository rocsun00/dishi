"""Real offline install/update/rollback and public distribution boundaries."""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


installer = module("dishi_installer", "install.py")
builder = module("dishi_builder", "build_release.py")
rules = installer.rules


def runtime_source(destination):
    """A real install input containing the runtime inputs, without source logs."""
    destination.mkdir()
    for path, relative in rules.inventory(ROOT):
        if rules.runtime_includes(relative):
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    return destination


class DistributionTests(unittest.TestCase):
    def test_overlap_is_rejected(self):
        with self.assertRaises(ValueError):
            installer.check_paths(ROOT, ROOT / "nested" / "dishi")

    def test_existing_install_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "skills" / "dishi"
            destination.mkdir(parents=True)
            sentinel = destination / "local-notes.txt"
            sentinel.write_text("keep my work", encoding="utf-8")
            with self.assertRaises(ValueError):
                installer.install(ROOT, destination)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep my work")

    def test_dry_run_makes_no_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "new-parent" / "skills" / "dishi"
            report = installer.install(ROOT, destination, dry_run=True)
            self.assertTrue(report["dry_run"])
            self.assertFalse(destination.parent.exists())

    def test_symlink_source_and_destination_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            source.mkdir()
            (source / "external").symlink_to(ROOT / "SKILL.md")
            with self.assertRaisesRegex(ValueError, "external"):
                installer.check_paths(source, Path(temp) / "dishi")
            destination = Path(temp) / "dishi"
            destination.symlink_to(source, target_is_directory=True)
            with self.assertRaises(ValueError):
                installer.check_paths(ROOT, destination)

    def test_non_directory_and_wrong_name_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "dishi"
            destination.write_text("not a directory", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not a directory"):
                installer.install(ROOT, destination, replace=True)
            with self.assertRaisesRegex(ValueError, "named 'dishi'"):
                installer.install(ROOT, Path(temp) / "wrong-name", dry_run=True)

    def test_filter_is_narrow_and_preserves_source_evidence(self):
        excluded = ["knowledge/验收覆盖-example.json", "knowledge/test/source/author_self_check.json",
                    "knowledge/test/source/draft_freeze.json", "knowledge/test/source/first_half_handoff.json"]
        kept = ["knowledge/test/source/api/author_self_check.json", "knowledge/test/source/source.json",
                "knowledge/test/source/fetch_manifest.json", "knowledge/test/source/extraction.json",
                "knowledge/test/source/chapter_map.json", "knowledge/test/source/ancient_notes.json",
                "knowledge/test/source/import_validation.json", "knowledge/test/质量说明.md"]
        for relative in excluded:
            self.assertTrue(rules.process_exclusion(relative), relative)
            self.assertFalse(rules.runtime_includes(relative), relative)
        original = b'{"path":"/' + b'Users/original-author/text", "sha256":"abc"}\n'
        for relative in kept:
            self.assertFalse(rules.process_exclusion(relative), relative)
            self.assertEqual(builder.release_bytes(relative, original), original, relative)
        self.assertFalse(rules.runtime_includes("knowledge/tests/test_kb.py"))
        self.assertFalse(rules.runtime_includes("scripts/build_release.py"))

    def test_private_workspace_redaction_is_scoped_to_declared_process_note(self):
        for prefix in ("/" + "Users/张三/work", "/" + "root/work", "/private/" + "tmp/work", "/private/" + "var/folders/work"):
            original = ("脚本在" + prefix + "，原著作者不变。\n").encode("utf-8")
            public = builder.release_bytes("knowledge/liezi/source/处理说明.md", original)
            self.assertNotIn(prefix.encode("utf-8"), public)
            self.assertIn("原著作者不变".encode("utf-8"), public)
            self.assertEqual(builder.release_bytes("knowledge/liezi/source/source.wikitext", original), original)

    def test_markdown_links_redirect_only_archived_local_targets(self):
        original = ("[coverage](../验收覆盖-示例.json#ids) [source](source/source.json) "
                    "[remote](https://example.test/knowledge/验收覆盖-示例.json) "
                    "[self](source/author_self_check.json)").encode("utf-8")
        public = builder.release_bytes("knowledge/test/质量说明.md", original).decode("utf-8")
        self.assertIn("[coverage](../../docs/provenance-summary.md#archived-records)", public)
        self.assertIn("[self](../../docs/provenance-summary.md#archived-records)", public)
        self.assertIn("[source](source/source.json)", public)
        self.assertIn("https://example.test/knowledge/验收覆盖-示例.json", public)

    def test_attribution_distinguishes_archived_source_hashes(self):
        original = {"works": [{"local_json_evidence_inventory": [
            {"file": "knowledge/test/source/author_self_check.json", "sha256": "abc"},
            {"file": "knowledge/test/source/extraction.json", "sha256": "def"}]}]}
        public = json.loads(builder.release_bytes("docs/source-attribution.json", json.dumps(original).encode()))
        archived, retained = public["works"][0]["local_json_evidence_inventory"]
        self.assertEqual(archived["source_sha256"], "abc")
        self.assertNotIn("sha256", archived)
        self.assertEqual(archived["distribution_status"], "archived_local_only")
        self.assertEqual(retained["sha256"], "def")
        self.assertEqual(original["works"][0]["local_json_evidence_inventory"][0]["sha256"], "abc")

    def test_public_path_scanner_rejects_concrete_paths_and_preserves_input(self):
        for path in ("/private/tmp/private-task", "/private/var/folders/private-task",
                     "/" + "Users/alice/project", "/" + "root/private-task",
                     "/" + "Users/alice/project/$TASK", "/private/tmp/private-task/$FILE"):
            with self.subTest(path=path):
                text = json.dumps({"path": path})
                result = rules.scan_public_text("docs/something.json", text)
                self.assertEqual(result["findings"][0]["location"], "$.path")
                self.assertEqual(result["findings"][0]["path"], path)
                self.assertFalse(result["allowed"])
                self.assertEqual(json.loads(text)["path"], path)
                with self.assertRaisesRegex(ValueError, "docs/something.json"):
                    rules.check_public_text("docs/something.json", text.encode())

    def test_public_path_scanner_allows_generic_documentation_and_reports_roles(self):
        generic = "Bare /private/tmp or /private/var; /Users/<user>/project; /root/<actor>; /Users/$USER/project; /private/tmp/$TASK/file; https://example.test/Users/name"
        self.assertFalse(rules.scan_public_text("docs/install.md", generic)["findings"])
        role = json.dumps({"fetched_by": "root agent: official HTTPS API"})
        result = rules.scan_public_text("knowledge/sanlue/source/fetch_manifest.json", role)
        self.assertFalse(result["findings"])
        self.assertEqual(result["allowed"][0]["location"], "$.fetched_by")
        injected = json.dumps({"fetched_by": "root agent uses /private/tmp/private-task"})
        result = rules.scan_public_text("knowledge/sanlue/source/fetch_manifest.json", injected)
        self.assertTrue(result["findings"])
        self.assertFalse(result["allowed"])
        upstream = json.dumps({"text": "Original source mentions /private/tmp/private-task"})
        self.assertTrue(rules.scan_public_text("knowledge/test/source/api/page.json", upstream)["findings"])
        for literal in ("workspace:/private/tmp/private-task", "file:///private/var/folders/private-task"):
            self.assertTrue(rules.scan_public_text("docs/paths.md", literal)["findings"])

    def test_release_rejects_private_path_in_any_public_json(self):
        with tempfile.TemporaryDirectory() as temp:
            source = runtime_source(Path(temp) / "source")
            for name in ("install.py", "package_rules.py"):
                target = source / "scripts" / name
                target.parent.mkdir(exist_ok=True)
                shutil.copyfile(ROOT / "scripts" / name, target)
            offending = source / "docs/something.json"
            original = json.dumps({"path": "/private/tmp/private-task"})
            offending.write_text(original)
            output = Path(temp) / "release"
            with self.assertRaisesRegex(ValueError, "docs/something.json"):
                builder.build(source, output)
            self.assertEqual(offending.read_text(), original)
            self.assertFalse(output.exists())
            self.assertFalse(list(Path(temp).glob("dishi-*.zip")))

    def test_backup_location_is_outside_scan_tree_and_custom_targets_stay_local(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp).resolve() / "fake-home"
            with mock.patch.object(Path, "home", return_value=home):
                for scope in (".agents", ".claude", ".codex"):
                    standard = home / scope / "skills" / "dishi"
                    self.assertEqual(installer.backup_directory(standard), home / ".local/share/dishi/backups")
                custom = Path(temp).resolve() / "project" / ".agents" / "skills" / "dishi"
                backups = installer.backup_directory(custom)
                self.assertNotIn(home, backups.parents)
                self.assertNotIn(custom.parent, backups.parents)
                self.assertEqual(backups, Path(temp).resolve() / "project/.dishi-backups/skills-installs")
                for specified in (custom.parent, custom.parent / "backup", custom / "backup"):
                    with self.assertRaisesRegex(ValueError, "outside"):
                        installer.backup_directory(custom, specified)

    def test_backup_symlink_cannot_hide_inside_scan_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp).resolve()
            destination = project / "skills" / "dishi"
            destination.parent.mkdir()
            (project / ".dishi-backups").symlink_to(destination.parent, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "outside"):
                installer.backup_directory(destination)
            with self.assertRaisesRegex(ValueError, "outside"):
                installer.backup_directory(destination, project / "other-host" / "skills" / "backups")

    def test_parent_creation_failure_does_not_leak_absolute_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            blocker = Path(temp) / "blocked"
            blocker.write_text("file")
            destination = blocker / "skills" / "dishi"
            with self.assertRaises(ValueError) as raised:
                installer.install(ROOT, destination)
            self.assertNotIn(str(Path(temp)), str(raised.exception))

    def test_actual_install_updates_backups_and_english_readback(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "skills" / "dishi"
            first = installer.install(ROOT, destination)
            self.assertEqual(first["books"], 27)
            self.assertIsNone(first["backup"])
            for name in rules.REQUIRED:
                self.assertTrue((destination / name).is_file(), name)
            self.assertFalse((destination / "tests").exists())
            self.assertFalse((destination / "knowledge/tests").exists())
            self.assertFalse((destination / "scripts").exists())
            self.assertFalse(list(destination.glob("knowledge/验收覆盖-*.json")))
            self.assertFalse(list(destination.glob("knowledge/*/source/author_self_check.json")))
            self.assertIn("provenance-summary.md#archived-records", (destination / "knowledge/知识库总览.md").read_text())
            sentinel = destination / "local-notes.txt"
            sentinel.write_text("local additions survive in backup", encoding="utf-8")
            second = installer.install(ROOT, destination, replace=True)
            backup = Path(second["backup"])
            self.assertNotIn(destination.parent, backup.parents)
            self.assertEqual((backup / "local-notes.txt").read_text(), "local additions survive in backup")
            self.assertFalse((destination / "local-notes.txt").exists())
            third = installer.install(ROOT, destination, replace=True, backup_dir=Path(temp) / "explicit-backups")
            self.assertTrue((backup / "local-notes.txt").exists())
            self.assertTrue(Path(third["backup"]).is_dir())
            self.assertEqual((destination / "knowledge/catalog.json").read_bytes(), (ROOT / "knowledge/catalog.json").read_bytes())
            result = subprocess.run([sys.executable, "-B", str(destination / "knowledge/kb.py"),
                                     "search", "trust and cooperation", "--json", "--limit", "2"],
                                    capture_output=True, text=True, encoding="utf-8", timeout=180)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout))

    def test_missing_required_files_are_named_and_preserve_existing_install(self):
        with tempfile.TemporaryDirectory() as temp:
            source = runtime_source(Path(temp) / "source")
            for name in ("knowledge/english_keywords.json", "knowledge/ranking.py", "docs/corpus.md", "docs/examples.zh-CN.md",
                         "docs/examples.en.md", "docs/provenance-summary.md", "references/research-method.md",
                         "references/research-examples.zh-CN.md", "references/research-examples.en.md"):
                with self.subTest(file=name):
                    path = source / name
                    original = path.read_bytes()
                    path.unlink()
                    destination = Path(temp) / "skills" / "dishi"
                    destination.mkdir(parents=True, exist_ok=True)
                    sentinel = destination / "old.txt"
                    sentinel.write_text("keep existing version")
                    with self.assertRaises(ValueError) as raised:
                        installer.install(source, destination, replace=True)
                    self.assertIn(name, str(raised.exception))
                    self.assertNotIn(str(source), str(raised.exception))
                    self.assertEqual(sentinel.read_text(), "keep existing version")
                    self.assertFalse((Path(temp) / ".dishi-backups").exists())
                    path.write_bytes(original)

    def test_actual_missing_source_file_has_relative_error_and_preserves_old_version(self):
        with tempfile.TemporaryDirectory() as temp:
            source = runtime_source(Path(temp) / "source")
            missing = "knowledge/lunyu/source/source.wikitext"
            (source / missing).unlink()
            destination = Path(temp) / "skills" / "dishi"
            destination.mkdir(parents=True)
            (destination / "old.txt").write_text("old version")
            with self.assertRaises(ValueError) as raised:
                installer.install(source, destination, replace=True)
            self.assertIn(missing, str(raised.exception))
            self.assertNotIn(str(Path(temp)), str(raised.exception))
            self.assertEqual((destination / "old.txt").read_text(), "old version")
            self.assertFalse(list(destination.parent.glob(".dishi-install-*")))

    def test_new_destination_during_validation_still_requires_replace(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "skills" / "dishi"
            real_run = installer.run_json

            def create_concurrent_install(payload, arguments, timeout, purpose):
                result = real_run(payload, arguments, timeout, purpose)
                if arguments[0] == "explain-query":
                    destination.mkdir()
                    (destination / "other-install.txt").write_text("preserve concurrent install")
                return result

            with mock.patch.object(installer, "run_json", side_effect=create_concurrent_install):
                with self.assertRaisesRegex(ValueError, "appeared during validation"):
                    installer.install(ROOT, destination)
            self.assertEqual((destination / "other-install.txt").read_text(), "preserve concurrent install")
            self.assertFalse((Path(temp) / ".dishi-backups").exists())

    def test_failed_final_swap_restores_old_version_and_keeps_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "skills" / "dishi"
            destination.mkdir(parents=True)
            (destination / "old.txt").write_text("old version")
            real_replace = installer.os.replace

            def fail_payload(source, target):
                if Path(source).name == "dishi" and Path(source).parent.name.startswith(".dishi-install-"):
                    raise OSError("simulated final swap failure")
                return real_replace(source, target)

            with mock.patch.object(installer.os, "replace", side_effect=fail_payload):
                with self.assertRaisesRegex(ValueError, "simulated final swap failure"):
                    installer.install(ROOT, destination, replace=True)
            self.assertEqual((destination / "old.txt").read_text(), "old version")
            copies = list((Path(temp) / ".dishi-backups").rglob("old.txt"))
            self.assertEqual(len(copies), 1)
            self.assertEqual(copies[0].read_text(), "old version")
            self.assertFalse(list(destination.parent.glob(".dishi-install-*")))

    def test_double_swap_failure_reports_retained_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "skills" / "dishi"
            destination.mkdir(parents=True)
            (destination / "old.txt").write_text("old version")
            real_replace = installer.os.replace

            def fail_commit_and_restore(source, target):
                if Path(source).parent.name.startswith(".dishi-install-"):
                    raise OSError("simulated commit/restore failure")
                return real_replace(source, target)

            with mock.patch.object(installer.os, "replace", side_effect=fail_commit_and_restore):
                with self.assertRaises(ValueError) as raised:
                    installer.install(ROOT, destination, replace=True)
            self.assertIn("preserved at <backups>/", str(raised.exception))
            self.assertNotIn(str(Path(temp)), str(raised.exception))
            self.assertEqual(len(list((Path(temp) / ".dishi-backups").rglob("old.txt"))), 1)

    def test_backup_creation_failure_preserves_old_install(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "skills" / "dishi"
            destination.mkdir(parents=True)
            (destination / "old.txt").write_text("old version")
            backup_file = Path(temp) / "backups-file"
            backup_file.write_text("not a directory")
            with self.assertRaises(ValueError) as raised:
                installer.install(ROOT, destination, replace=True, backup_dir=backup_file)
            self.assertNotIn(str(Path(temp)), str(raised.exception))
            self.assertEqual((destination / "old.txt").read_text(), "old version")

    def test_invalid_validator_json_or_timeout_never_replaces_old_install(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "skills" / "dishi"
            destination.mkdir(parents=True)
            (destination / "old.txt").write_text("old version")
            for result in (subprocess.CompletedProcess([], 0, "not json", ""),
                           subprocess.TimeoutExpired(["private-command"], 180)):
                with self.subTest(result=type(result).__name__):
                    options = {"side_effect": result} if isinstance(result, Exception) else {"return_value": result}
                    with mock.patch.object(installer.subprocess, "run", **options):
                        with self.assertRaises(ValueError):
                            installer.install(ROOT, destination, replace=True)
                    self.assertEqual((destination / "old.txt").read_text(), "old version")
                    self.assertFalse((Path(temp) / ".dishi-backups").exists())

    def test_temp_release_manifest_and_runtime_install_preserve_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "public"
            evidence = {relative: hashlib.sha256(path.read_bytes()).hexdigest()
                        for path, relative in rules.inventory(ROOT) if "/source/" in relative}
            report = builder.build(ROOT, output)
            manifest = json.loads((output / "RELEASE_MANIFEST.json").read_text())
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(report["excluded_records"], len(manifest["excluded_local_records"]))
            self.assertGreater(report["excluded_bytes"], 14_000_000)
            for record in manifest["files"]:
                self.assertEqual(hashlib.sha256((output / record["path"]).read_bytes()).hexdigest(), record["sha256"])
            for record in manifest["excluded_local_records"]:
                self.assertFalse((output / record["path"]).exists())
                self.assertTrue((ROOT / record["path"]).is_file())
                self.assertEqual(hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest(), record["source_sha256"])
            for relative, before in evidence.items():
                self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), before)
                if not rules.process_exclusion(relative) and relative not in rules.PROCESS_PATH_NOTES:
                    self.assertEqual((output / relative).read_bytes(), (ROOT / relative).read_bytes(), relative)
            with zipfile.ZipFile(report["archive"]) as archive:
                self.assertIn("dishi/docs/provenance-summary.md", archive.namelist())
                self.assertFalse(any("/验收覆盖-" in name for name in archive.namelist()))
            installed = Path(temp) / "skills" / "dishi"
            self.assertEqual(installer.install(output, installed)["books"], 27)
            self.assertFalse((installed / "scripts").exists())
            self.assertFalse((installed / "RELEASE_MANIFEST.json").exists())
            with self.assertRaises(ValueError):
                builder.build(ROOT, output)


if __name__ == "__main__":
    unittest.main()
