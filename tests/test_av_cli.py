"""Offline CLI tests: python3 -m unittest discover -s tests -v."""
from io import BytesIO, StringIO
from contextlib import redirect_stdout
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("av_cli", ROOT / "scripts" / "av.py")
av = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(av)


class TestAvCLI(unittest.TestCase):
    def test_semver(self):
        self.assertTrue(av.parse_version("0.4.0") > av.parse_version("0.3.1"))
        for bad in ("v1.0.0", "1.0", "0.3.0-rc.1", "1.02.3"):
            with self.assertRaises(ValueError):
                av.parse_version(bad)

    def test_cached_version(self):
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": temp}):
                with mock.patch.object(av, "get_remote_version", return_value="0.4.0"):
                    with mock.patch.object(av, "manifest", return_value={"version": "0.3.0"}):
                        out = StringIO()
                        with redirect_stdout(out):
                            av.check_update()
                        self.assertTrue(json.loads(out.getvalue())["update_available"])
                        self.assertEqual(av.load_cache()["latest_version"], "0.4.0")
                        with mock.patch.object(av.subprocess, "Popen") as bg:
                            av.schedule_check()
                            bg.assert_not_called()

    def test_background_nonblocking(self):
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": temp}):
                with mock.patch.object(av.subprocess, "Popen") as bg:
                    av.schedule_check()
                    av.schedule_check()
                    bg.assert_called_once()

    def test_report_forwarding(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "repo"
            project.mkdir()
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            env = {**os.environ, "AV_DISABLE_UPDATE_CHECK": "1"}
            def call(*args):
                p = subprocess.run([sys.executable, str(ROOT / "scripts" / "av.py"),
                                    "--project", str(project), "report", *args],
                                   text=True, capture_output=True, env=env)
                self.assertEqual(p.returncode, 0, p.stderr)
                return json.loads(p.stdout)
            first = call("start", "--task-id", "T-101", "--task", "Review a task")
            call("finding", "--task-id", "T-101", "--title", "Issue A")
            call("finish", "--task-id", "T-101", "--assessment", "READY")
            second = call("start", "--task-id", "T-101", "--task", "Review a task")
            self.assertEqual(first["json"], second["json"])
            self.assertEqual(second["round"], 2)

    def archive(self, entries):
        buf = BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as archive:
            for name, contents, type_ in entries:
                m = tarfile.TarInfo("Adversarial-verification-SKILL-test/" + name)
                if type_ == "link":
                    m.type = tarfile.SYMTYPE
                    m.linkname = "/etc/passwd"
                    archive.addfile(m)
                else:
                    m.size = len(contents)
                    archive.addfile(m, BytesIO(contents))
        return buf.getvalue()

    def test_tar_rejects_traversal_and_links(self):
        with tempfile.TemporaryDirectory() as temp:
            for name, type_ in (("../outside", "file"), ("link", "link")):
                with self.assertRaises(ValueError):
                    av.extract_archive(self.archive([(name, b"x", type_)]), Path(temp))

    def test_refuse_update_inside_git_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            installed = Path(temp) / "skill"
            installed.mkdir()
            subprocess.run(["git", "init", "-q", str(installed)], check=True)
            with mock.patch.object(av, "ROOT", installed):
                with self.assertRaisesRegex(ValueError, "git pull"):
                    av.update(yes=True)

    def test_update_pinned_archive_and_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            installed = Path(temp) / "skill"
            installed.mkdir()
            (installed / "SKILL.md").write_text("old", encoding="utf-8")
            (installed / "skill-version.json").write_text(
                json.dumps({"repository": av.REPO, "version": "0.2.0"}), encoding="utf-8")
            required = [
                ("SKILL.md", b"new", "file"),
                ("skill-version.json", json.dumps({"repository": av.REPO, "version": "0.4.0"}).encode(), "file"),
                ("scripts/av.py", b"x", "file"),
                ("scripts/review_report.py", b"x", "file"),
                ("templates/review-report.html", b"x", "file"),
            ]
            latest_commit = "a" * 40
            def fake_json(url):
                return {"sha": latest_commit} if url == av.COMMITS else {"repository": av.REPO, "version": "0.4.0"}
            with mock.patch.object(av, "ROOT", installed):
                with mock.patch.object(av, "fetch_json", side_effect=fake_json):
                    with mock.patch.object(av, "fetch", return_value=self.archive(required)):
                        with mock.patch.object(av, "cache_remote", return_value={}):
                            with redirect_stdout(StringIO()):
                                self.assertEqual(av.update(yes=True), 0)
            self.assertEqual((installed / "SKILL.md").read_text(), "new")
            backups = list(installed.parent.glob(".av-backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / "SKILL.md").read_text(), "old")

    def test_windows_launcher_install_and_reinstall(self):
        with tempfile.TemporaryDirectory() as temp:
            with redirect_stdout(StringIO()):
                self.assertEqual(av.install_launcher(dest=temp, windows=True), 0)
            file = Path(temp) / "av.cmd"
            self.assertTrue(file.exists())
            content = file.read_text(encoding="utf-8")
            self.assertIn("@echo off", content)
            self.assertIn("REM Adversarial Verification launcher", content)
            self.assertIn(" %*", content)
            self.assertIn("exit /b %errorlevel%", content)
            with redirect_stdout(StringIO()):
                self.assertEqual(av.install_launcher(dest=temp, windows=True), 0)
            file.write_text("@echo off\necho unrelated tool\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Refusing to replace another program"):
                av.install_launcher(dest=temp, windows=True)

    def test_windows_launcher_quotes_paths_and_escaped_percent(self):
        with mock.patch.object(av.sys, "executable", r"C:\Program Files\Python312\python.exe"):
            body = av.launcher_body(windows=True)
            self.assertIn('"C:\\Program Files\\Python312\\python.exe"', body)
            self.assertIn('"', body)
            self.assertIn(" %*", body)
            self.assertIn("REM Adversarial Verification launcher", body)

    def test_valid_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            entries = [
                ("SKILL.md", b"skill", "file"),
                ("skill-version.json", json.dumps({"repository": av.REPO, "version": "0.4.0"}).encode(), "file"),
                ("scripts/av.py", b"x", "file"),
                ("scripts/review_report.py", b"x", "file"),
                ("templates/review-report.html", b"x", "file"),
            ]
            self.assertEqual(av.extract_archive(self.archive(entries), Path(temp)), "0.4.0")


if __name__ == "__main__":
    unittest.main()
