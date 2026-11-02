"""Review decision lifecycle and HTML copy-surface tests (offline)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "av.py"
SCHEMA = "adversarial-verification-import/v1"


class DecisionReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.env = {**os.environ, "AV_DISABLE_UPDATE_CHECK": "1"}
        self.task_id = "DEC-42"
        self.start = self.cmd("start", "--task-id", self.task_id,
                              "--task", "Permission package cloning", "--risk", "5",
                              "--agents", "2")

    def cmd(self, action, *arguments, success=True):
        p = subprocess.run(
            [sys.executable, str(CLI), "--project", str(self.project),
             "report", action, *arguments],
            text=True, capture_output=True, env=self.env
        )
        if not success:
            self.assertNotEqual(p.returncode, 0)
            return p.stderr
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def read(self):
        return json.loads(Path(self.start["json"]).read_text(encoding="utf-8"))

    def batch(self, filename, content):
        file = Path(self.tmp.name) / filename
        file.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        return str(file)

    def test_decision_lifecycle_and_distinct_bug_count(self):
        args = ("--task-id", self.task_id, "--title", "Can disabled packages be cloned?",
                "--context", "Permission package cloning", "--scenario", "Disabled source package",
                "--question", "Should cloning be allowed?",
                "--blocking", "--kind", "requirement-gap",
                "--options-json", json.dumps([
                    {"id": "A", "text": "Allow", "tradeoff": "Propagates disabled settings"},
                    {"id": "B", "text": "Reject", "tradeoff": "Needs clear user feedback"}
                ]))
        decision = self.cmd("decision", "add", *args)
        self.assertEqual(decision["decision_id"], "D001")
        duplicate = self.cmd("decision", "add", *args)
        self.assertEqual(duplicate["decision_id"], "D001")
        self.assertEqual(duplicate["action"], "updated_decision")
        data = self.read()
        self.assertEqual(len(data["findings"]), 0)
        self.assertEqual(len(data["decisions"]), 1)
        self.assertEqual(data["decisions"][0]["status"], "pending")
        self.assertTrue(data["decisions"][0]["blocking"])
        html = Path(self.start["html"]).read_text(encoding="utf-8")
        self.assertIn("待你确认", html)
        self.assertIn("复制全部待确认事项", html)
        self.assertIn("复制问题，交给 AI 讨论", html)
        self.assertIn("复制完整上下文", html)
        self.assertIn("data.decisions||[]", html)
        self.assertIn('"decisions":[{"id":"D001"', html)
        self.assertIn('"findings":[]', html)
        self.assertNotIn("new QRcode", html)
        self.cmd("finish", "--task-id", self.task_id, "--assessment", "NEEDS_DECISION")
        self.cmd("start", "--task-id", self.task_id,
                 "--task", "Permission package cloning")
        missing_source = self.cmd("decision", "resolve", "--task-id", self.task_id,
                                  "--id", "D001", "--answer", "Reject",
                                  "--source", "", success=False)
        self.assertIn("confirmation source", missing_source)
        resolved = self.cmd("decision", "resolve", "--task-id", self.task_id,
                            "--id", "D001", "--answer", "Reject disabled packages",
                            "--source", "User explicitly confirmed in task thread")
        self.assertEqual(resolved["status"], "resolved")
        self.assertIn("already closed", self.cmd(
            "decision", "resolve", "--task-id", self.task_id, "--id", "D001",
            "--answer", "Override", "--source", "Test", success=False))
        self.assertEqual(self.read()["decisions"][0]["resolution"]["round"], 2)
        self.assertEqual(len(self.read()["decisions"][0]["history"]), 1)

    def test_legacy_report_without_decisions_is_compatible(self):
        data = self.read()
        del data["decisions"]
        Path(self.start["json"]).write_text(json.dumps(data), encoding="utf-8")
        first = self.cmd("decision", "add", "--task-id", self.task_id,
                         "--title", "Legacy fallback question", "--kind", "feedback")
        self.assertEqual(first["decision_id"], "D001")
        self.assertEqual(len(self.read()["decisions"]), 1)

    def test_batch_import_and_dry_run_are_atomic(self):
        payload = {
            "schema": SCHEMA,
            "decisions": [
                {"key": "inactive", "title": "What about disabled packages?",
                 "kind": "ambiguity", "context": "Cloning",
                 "question": "Allow clones?", "blocking": True,
                 "options": [{"id": "A", "text": "Allow"}]}
            ],
            "resolutions": [{
                "ref": "inactive", "answer": "Allow with existing constraints",
                "source": "User confirmation in conversation"
            }]
        }
        path = self.batch("batch.json", payload)
        preview = self.cmd("import", "--task-id", self.task_id,
                           "--file", path, "--dry-run")
        self.assertEqual(preview["action"], "validated_batch")
        self.assertEqual(self.read()["decisions"], [])
        success = self.cmd("import", "--task-id", self.task_id, "--file", path)
        self.assertEqual(success["decision_ids"], ["D001"])
        self.assertEqual(success["resolved_ids"], ["D001"])
        self.assertEqual(self.read()["decisions"][0]["status"], "resolved")
        self.assertEqual(self.cmd("import", "--task-id", self.task_id,
                                  "--file", path)["action"], "already_imported")

    def test_invalid_batch_rolls_back_all_records(self):
        bad = {
            "schema": SCHEMA,
            "decisions": [
                {"key": "one", "title": "Question", "kind": "feedback"},
                {"key": "other", "title": "Missing scenario",
                 "options": [{"id": "A", "text": "ok"}, {"id": "A", "text": "bad"}]}
            ]
        }
        before = Path(self.start["json"]).read_bytes()
        err = self.cmd("import", "--task-id", self.task_id, "--file",
                       self.batch("invalid.json", bad), success=False)
        self.assertIn("Invalid or duplicate", err)
        self.assertEqual(Path(self.start["json"]).read_bytes(), before)

    def test_untrusted_text_is_script_escaped_and_not_bug(self):
        self.cmd("decision", "add", "--task-id", self.task_id,
                 "--title", '</script><script>alert("bad")</script>',
                 "--question", "Review <unsafe> message")
        rendered = Path(self.start["html"]).read_text(encoding="utf-8")
        self.assertNotIn('</script><script>alert("bad")</script>', rendered)
        self.assertIn("\\u003cscript", rendered)
        self.assertEqual(len(self.read()["findings"]), 0)


if __name__ == "__main__":
    unittest.main()
