"""Batch import tests with no remote network or project mutations outside test repos."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "scripts" / "av.py"


class TestBatchImport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.env = {**os.environ, "AV_DISABLE_UPDATE_CHECK": "1"}
        self.task_id = "TASK-17"

    def run_cli(self, *args, success=True):
        p = subprocess.run([sys.executable, str(CLI), "--project", str(self.project),
                            "report", *args], text=True, capture_output=True, env=self.env)
        if not success:
            self.assertNotEqual(p.returncode, 0)
            return p.stderr
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def payload(self, name, value):
        path = Path(self.temp.name) / name
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def start(self):
        return self.run_cli("start", "--task-id", self.task_id,
                            "--task", "Review user permissions", "--risk", "4", "--agents", "2")

    def test_dry_run_import_finding_fix_events_and_repeated_batch(self):
        report = self.start()
        payload = self.payload("first.json", {
            "schema": "adversarial-verification-import/v1",
            "findings": [
                {"key": "auth", "title": "Missing ownership check",
                 "category": "authorization", "severity": "high",
                 "attribution": "introduced", "reviewer": "Agent C",
                 "evidence": "No ownership validation", "proposal": "Check owner"},
                {"key": "query", "title": "N+1 queries", "severity": "medium",
                 "evidence": "One query per order", "proposal": "Batch reads"}
            ],
            "fixes": [{"ref": "auth", "status": "verified",
                       "description": "Added validation", "verification": "Negative test passed"}],
            "events": [{"kind": "test", "text": "Regression suite passed"}]
        })
        preview = self.run_cli("import", "--task-id", self.task_id,
                               "--file", payload, "--dry-run")
        self.assertEqual(preview["action"], "validated_batch")
        source = json.loads(Path(report["json"]).read_text(encoding="utf-8"))
        self.assertEqual(len(source["findings"]), 0)
        imported = self.run_cli("import", "--task-id", self.task_id, "--file", payload)
        self.assertEqual(imported["action"], "imported_batch")
        self.assertEqual(imported["finding_ids"], ["F001", "F002"])
        self.assertEqual(imported["fixed_ids"], ["F001"])
        repeated = self.run_cli("import", "--task-id", self.task_id, "--file", payload)
        self.assertEqual(repeated["action"], "already_imported")
        self.assertEqual(repeated["json"], report["json"])
        archive = json.loads(Path(report["json"]).read_text(encoding="utf-8"))
        self.assertEqual(len(archive["sessions"]), 1)
        self.assertEqual(len(archive["findings"]), 2)
        self.assertEqual(archive["findings"][0]["status"], "verified")
        self.assertEqual(len(archive["findings"][0]["repairs"]), 1)
        self.assertTrue(Path(report["html"]).exists())

    def test_atomic_failure_does_not_modify_report(self):
        report = self.start()
        before = Path(report["json"]).read_bytes()
        invalid = self.payload("bad.json", {
            "schema": "adversarial-verification-import/v1",
            "findings": [{"key": "bad", "title": "Issue"}],
            "fixes": [{"ref": "missing", "description": "Fake fix"}]
        })
        error = self.run_cli("import", "--task-id", self.task_id, "--file", invalid, success=False)
        self.assertIn("Unknown finding key", error)
        self.assertEqual(Path(report["json"]).read_bytes(), before)

    def test_import_existing_finding_id_and_round_reuse(self):
        first = self.start()
        self.run_cli("finding", "--task-id", self.task_id,
                     "--title", "Original", "--category", "correctness")
        payload = self.payload("update.json", {
            "schema": "adversarial-verification-import/v1",
            "findings": [{"id": "F001", "title": "Updated",
                          "category": "correctness", "evidence": "New evidence"}]
        })
        self.run_cli("import", "--task-id", self.task_id, "--file", payload)
        self.run_cli("finish", "--task-id", self.task_id, "--assessment", "CHANGES_NEEDED")
        self.start()
        imported = self.run_cli("import", "--task-id", self.task_id, "--file", payload)
        self.assertEqual(imported["action"], "imported_batch")
        data = json.loads(Path(first["json"]).read_text(encoding="utf-8"))
        self.assertEqual(len(data["sessions"]), 2)
        self.assertEqual(len(data["findings"]), 1)
        self.assertEqual(data["findings"][0]["title"], "Updated")

    def test_reject_malformed_and_unexpected_inputs(self):
        self.start()
        samples = [
            {"schema": "invalid", "findings": [{"title": "x"}]},
            {"schema": "adversarial-verification-import/v1", "findings": "wrong"},
            {"schema": "adversarial-verification-import/v1",
             "findings": [{"title": "x", "severity": "fake"}]},
            {"schema": "adversarial-verification-import/v1",
             "fixes": [{"id": "F001", "description": "x", "status": "verified"}]},
            {"schema": "adversarial-verification-import/v1",
             "events": [{"kind": "bad", "text": "x"}]},
            {"schema": "adversarial-verification-import/v1",
             "findings": [{"title": "x", "typo": "y"}]},
            {"schema": "adversarial-verification-import/v1"}
        ]
        for i, sample in enumerate(samples):
            with self.subTest(i=i):
                file = self.payload(f"wrong-{i}.json", sample)
                self.run_cli("import", "--task-id", self.task_id,
                             "--file", file, success=False)


if __name__ == "__main__":
    unittest.main()
