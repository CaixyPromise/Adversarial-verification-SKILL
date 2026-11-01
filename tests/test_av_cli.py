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
