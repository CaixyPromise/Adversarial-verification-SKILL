"""Offline review report smoke tests. Run: python3 -m unittest discover -s tests -v."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "review_report.py"


class ReviewReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "test-repo"
        self.project.mkdir()
        if not shutil.which("git"):
            self.skipTest("git unavailable")
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.id = ["--task-id", "ISSUE-123"]

    def run_cli(self, *args, success=True):
        p = subprocess.run([sys.executable, str(SCRIPT), "--project", str(self.project), *args],
                           text=True, capture_output=True)
        if not success:
            self.assertNotEqual(p.returncode, 0)
            return p.stderr
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def test_reuse_reopen_and_exclusion(self):
        first = self.run_cli("start", *self.id, "--task", "Permission clone", "--risk", "5", "--agents", "2")
        resumed = self.run_cli("start", *self.id, "--task", "Permission clone")
        self.assertEqual(resumed["action"], "continued_existing_round")
        issue = self.run_cli("finding", *self.id, "--title", "Missing ownership check",
                             "--category", "auth", "--severity", "high",
                             "--evidence", "<script>alert(1)</script>", "--proposal", "Check owner")
        self.assertEqual(issue["finding_id"], "F001")
        self.run_cli("fix", *self.id, "--id", "F001", "--status", "verified",
                     "--description", "Added check", "--verification", "Negative case passed")
        self.run_cli("finish", *self.id, "--assessment", "READY")
        next_round = self.run_cli("start", *self.id, "--task", "Permission clone")
        self.assertEqual(next_round["json"], first["json"])
        self.assertEqual(next_round["round"], 2)
        again = self.run_cli("finding", *self.id, "--title", "Missing ownership check",
                             "--category", "auth", "--evidence", "Observed regression")
        self.assertEqual(again["action"], "reopened_existing_finding")
        self.assertEqual(again["finding_id"], "F001")
        self.run_cli("finish", *self.id, "--assessment", "CHANGES_NEEDED")
        archive = json.loads(Path(first["json"]).read_text(encoding="utf-8"))
        self.assertEqual(len(archive["sessions"]), 2)
        self.assertEqual(len(archive["findings"]), 1)
        self.assertEqual(archive["findings"][0]["status"], "open")
        self.assertEqual(len(archive["findings"][0]["repairs"]), 1)
        html = Path(first["html"]).read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("__REPORT_DATA__", html)
        self.assertEqual(len(list(Path(first["json"]).parent.glob("review-*.json"))), 1)
        self.assertEqual(len(list(Path(first["html"]).parent.glob("review-*.html"))), 1)
        ignored = subprocess.run(["git", "-C", str(self.project), "check-ignore",
                                  "-q", first["json"]])
        self.assertEqual(ignored.returncode, 0)

    def test_token_source_is_required_and_missing_usage_remains_unknown(self):
        first = self.run_cli("start", *self.id, "--task", "Review costs")
        err = self.run_cli("finish", *self.id, "--assessment", "READY",
                           "--input-tokens", "100", success=False)
        self.assertIn("--token-source", err)
        self.run_cli("finish", *self.id, "--assessment", "READY",
                     "--input-tokens", "100", "--output-tokens", "25",
                     "--token-source", "verified run counter")
        self.run_cli("start", *self.id, "--task", "Review costs")
        self.run_cli("finish", *self.id, "--assessment", "READY")
        d = json.loads(Path(first["json"]).read_text(encoding="utf-8"))
        self.assertEqual(d["sessions"][0]["input_tokens"], 100)
        self.assertEqual(d["sessions"][0]["token_source"], "verified run counter")
        self.assertIsNone(d["sessions"][1]["input_tokens"])

    def test_same_task_id_across_feature_branches(self):
        first = self.run_cli("start", *self.id, "--task", "One requirement")
        self.run_cli("finish", *self.id, "--assessment", "PARTIAL")
        subprocess.run(["git", "-C", str(self.project), "checkout", "-q", "-b", "feature/other"], check=True)
        again = self.run_cli("start", *self.id, "--task", "One requirement")
        self.assertEqual(first["json"], again["json"])


if __name__ == "__main__":
    unittest.main()
