#!/usr/bin/env python3
"""Offline review dossier: one task -> one reusable JSON + static HTML report.

Python 3.9+, standard library only. No network, web server, or model-token estimates.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

SCHEMA = "adversarial-verification-report/v1"
MARKER = ".adversarial-review-archive"
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", ".next", "target", "__pycache__"}
STATUSES = ("open", "fixed", "verified", "wontfix", "needs-decision")
ASSESSMENTS = ("READY", "CHANGES_NEEDED", "NEEDS_DECISION", "PARTIAL")
SEVERITIES = ("critical", "high", "medium", "low", "info")


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def git(project, *args):
    try:
        r = subprocess.run(["git", "-C", str(project), *args], capture_output=True,
                           text=True, timeout=5, check=False)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def project_root(path):
    resolved = Path(path).expanduser().resolve()
    return Path(git(resolved, "rev-parse", "--show-toplevel") or resolved).resolve()


def normalized(value):
    return " ".join(value.strip().casefold().split())


def slug(value):
    s = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (s[:42] or "task")


def identity(project, args):
    if getattr(args, "task_id", None):
        return "id:" + normalized(args.task_id)
    branch = git(project, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch and branch not in ("main", "master", "trunk", "develop", "development"):
        return "branch:" + branch
    task = getattr(args, "task", None)
    if task:
        return "task:" + normalized(task)
    raise ValueError("Provide --task-id (recommended), or --task on a default branch.")


def is_same_skill_archive(folder):
    if (folder / MARKER).is_file():
        return True
    if not folder.is_dir():
        return False
    for report in list(folder.glob("review-*.json"))[:12]:
        try:
            if json.loads(report.read_text(encoding="utf-8")).get("schema") == SCHEMA:
                return True
        except (OSError, ValueError, TypeError):
            pass
    return False


def tracked_under(project, folder):
    try:
        rel = folder.resolve().relative_to(project).as_posix()
    except ValueError:
        return False
    return bool(git(project, "ls-files", "--cached", "--", rel))


def discover_dir(project):
    preferred = [
        project / ".adversarial-verification" / "reports",
        project / ".review-reports",
        project / "reviews" / "adversarial-verification",
        project / "reports" / "adversarial-verification",
    ]
    for folder in preferred:
        if is_same_skill_archive(folder) and not tracked_under(project, folder):
            return folder
    # Bounded project-local discovery; never roam home or dependency trees.
    for base, dirs, files in os.walk(project):
        current = Path(base)
        depth = len(current.relative_to(project).parts)
        dirs[:] = [d for d in sorted(dirs) if d not in SKIP_DIRS and depth < 3]
        if MARKER in files or any(f.startswith("review-") and f.endswith(".json") for f in files):
            if is_same_skill_archive(current) and not tracked_under(project, current):
                return current
    for folder in preferred:
        if not tracked_under(project, folder):
            return folder
    raise RuntimeError("No safe untracked local report directory is available.")


def ensure_git_exclusion(project, folder):
    gitroot = git(project, "rev-parse", "--show-toplevel")
    if not gitroot:
        return
    root = Path(gitroot).resolve()
    try:
        relative = folder.resolve().relative_to(root).as_posix()
    except ValueError:
        return  # outside Git, never tracked by this repository
    if tracked_under(root, folder):
        raise RuntimeError("Report folder contains Git-tracked files; refusing to overwrite them.")
    raw_path = git(root, "rev-parse", "--git-path", "info/exclude")
    if not raw_path:
        raise RuntimeError("Cannot locate Git local exclude file; refusing to create report.")
    exclude = Path(raw_path)
    if not exclude.is_absolute():
        exclude = root / exclude
    exclude.parent.mkdir(parents=True, exist_ok=True)
    line = "/" + relative + "/"
    old = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    if line not in old.splitlines():
        with exclude.open("a", encoding="utf-8") as fh:
            fh.write(("" if not old or old.endswith("\n") else "\n")
                     + "# Local Adversarial Verification reports (never commit)\n" + line + "\n")
    probe = relative + "/review-ignore-probe.json"
    if git(root, "check-ignore", "--no-index", "--", probe) is None:
        raise RuntimeError("Git report exclusion could not be verified; refusing to write reports.")


def report_paths(project, args, create=False):
    folder = discover_dir(project)
    if create:
        ensure_git_exclusion(project, folder)
        folder.mkdir(parents=True, exist_ok=True)
        marker = folder / MARKER
        if not marker.exists():
            marker.write_text(SCHEMA + "\n", encoding="utf-8")
    key = identity(project, args)
    digest = hashlib.sha256((str(project) + "\n" + key).encode()).hexdigest()[:12]
    readable = key.split(":", 1)[1]
    stem = "review-" + slug(readable) + "-" + digest
    return folder / (stem + ".json"), folder / (stem + ".html"), key


def write_atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".report-", suffix=".tmp", delete=False) as temp:
        temp.write(content)
        tmp = Path(temp.name)
    os.replace(tmp, path)


def load(path):
    if not path.exists():
        raise ValueError("No existing task report. Run 'start' with the same --task-id first.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError("Unrecognized review-report schema; refusing to overwrite.")
    return data


def active_session(data):
    for session in reversed(data.get("sessions", [])):
        if session.get("ended_at") is None:
            return session
    raise ValueError("No active review round. Run 'start' to resume the same task report.")


def render(data, html_path):
    template = Path(__file__).resolve().parent.parent / "templates" / "review-report.html"
    html = template.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Safe embedding inside an inline JS script, including untrusted finding text.
    payload = (payload.replace("<", "\\u003c").replace(">", "\\u003e")
               .replace("&", "\\u0026").replace("\u2028", "\\u2028")
               .replace("\u2029", "\\u2029"))
    if html.count("__REPORT_DATA__") != 1:
        raise ValueError("Invalid HTML report template placeholder.")
    write_atomic(html_path, html.replace("__REPORT_DATA__", payload))


def store(data, json_path, html_path):
    data["updated_at"] = now()
    write_atomic(json_path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    render(data, html_path)


def cmd_start(args, project, json_path, html_path, key):
    if json_path.exists():
        data = load(json_path)
        if data["identity"] != key:
            raise ValueError("Task identity mismatch.")
    else:
        if not args.task:
            raise ValueError("--task is required when creating the first report.")
        data = {
            "schema": SCHEMA, "identity": key, "task_id": args.task_id,
            "task": args.task, "project": project.name,
            "created_at": now(), "updated_at": now(),
            "sessions": [], "findings": []
        }
    if data["sessions"] and data["sessions"][-1].get("ended_at") is None:
        session = data["sessions"][-1]
        action = "continued_existing_round"
    else:
        session = {
            "round": len(data["sessions"]) + 1, "started_at": now(), "ended_at": None,
            "risk_score": args.risk, "agents": args.agents, "assessment": None,
            "summary": "", "input_tokens": None, "output_tokens": None,
            "token_source": None, "events": []
        }
        data["sessions"].append(session)
        action = "started_new_round_in_existing_report" if json_path.exists() else "created_report"
    store(data, json_path, html_path)
    return {"action": action, "round": session["round"], "findings": [
        {"id": f["id"], "title": f["title"], "status": f["status"]}
        for f in data["findings"]
    ]}


def cmd_finding(args, data):
    session = active_session(data)
    selected = None
    if args.id:
        selected = next((f for f in data["findings"] if f["id"] == args.id), None)
        if selected is None:
            raise ValueError("Finding ID not found; omit --id to create a new finding.")
    else:
        selected = next((f for f in data["findings"]
                         if normalized(f["title"]) == normalized(args.title)
                         and normalized(f["category"]) == normalized(args.category)), None)
    if selected:
        was_resolved = selected["status"] in ("fixed", "verified", "wontfix")
        selected.update({
            "title": args.title, "category": args.category, "severity": args.severity,
            "attribution": args.attribution, "evidence": args.evidence,
            "proposal": args.proposal, "reviewer": args.reviewer,
            "status": "open", "last_seen_round": session["round"]
        })
        action = "reopened_existing_finding" if was_resolved else "updated_existing_finding"
    else:
        seq = max([int(f["id"][1:]) for f in data["findings"] if re.fullmatch(r"F\d+", f["id"])] or [0]) + 1
        selected = {
            "id": "F" + str(seq).zfill(3), "title": args.title,
            "category": args.category, "severity": args.severity, "attribution": args.attribution,
            "evidence": args.evidence, "proposal": args.proposal, "reviewer": args.reviewer,
            "status": "open", "first_seen_round": session["round"],
            "last_seen_round": session["round"], "repairs": []
        }
        data["findings"].append(selected)
        action = "created_finding"
    session["events"].append({"at": now(), "kind": "review",
                              "text": selected["id"] + ": " + action + " — " + args.title})
    return {"action": action, "finding_id": selected["id"]}


def cmd_fix(args, data):
    session = active_session(data)
    found = next((f for f in data["findings"] if f["id"] == args.id), None)
    if found is None:
        raise ValueError("Unknown finding ID: " + args.id)
    found["status"] = args.status
    found.setdefault("repairs", []).append({
        "round": session["round"], "at": now(), "status": args.status,
        "description": args.description, "verification": args.verification,
        "actor": args.actor
    })
    session["events"].append({"at": now(), "kind": "fix",
                              "text": args.id + " → " + args.status + ": " + args.description})
    return {"action": "recorded_fix", "finding_id": args.id, "status": args.status}


def cmd_event(args, data):
    session = active_session(data)
    session["events"].append({"at": now(), "kind": args.kind, "text": args.text})
    return {"action": "recorded_event", "round": session["round"]}


def cmd_finish(args, data):
    session = active_session(data)
    if args.input_tokens is not None or args.output_tokens is not None:
        if not args.token_source:
            raise ValueError("--token-source is required when recording token usage.")
        if any(v is not None and v < 0 for v in (args.input_tokens, args.output_tokens)):
            raise ValueError("Token usage cannot be negative.")
        session["input_tokens"] = args.input_tokens
        session["output_tokens"] = args.output_tokens
        session["token_source"] = args.token_source
    session["ended_at"] = now()
    session["assessment"] = args.assessment
    session["summary"] = args.summary or ""
    return {"action": "finished_round", "round": session["round"], "assessment": args.assessment}


def main():
    parser = argparse.ArgumentParser(description="Manage one offline HTML/JSON report per review task")
    parser.add_argument("--project", default=".", help="Target project directory (default: current repository)")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("start", "finding", "fix", "event", "finish", "render", "show"):
        p = sub.add_parser(name)
        p.add_argument("--task-id", help="Stable issue/requirement key; use on every run (recommended)")
        p.add_argument("--task", help="Task title; required on first start, optional later")
        if name == "start":
            p.add_argument("--risk", type=int, choices=range(7))
            p.add_argument("--agents", type=int, choices=range(4))
        elif name == "finding":
            p.add_argument("--id", help="Existing F### ID to update")
            p.add_argument("--title", required=True)
            p.add_argument("--category", default="correctness")
            p.add_argument("--severity", choices=SEVERITIES, default="medium")
            p.add_argument("--attribution", choices=("introduced", "worsened", "pre-existing", "unknown"), default="unknown")
            p.add_argument("--evidence", default="")
            p.add_argument("--proposal", default="")
            p.add_argument("--reviewer", default="")
        elif name == "fix":
            p.add_argument("--id", required=True)
            p.add_argument("--status", choices=STATUSES, default="fixed")
            p.add_argument("--description", required=True)
            p.add_argument("--verification", default="")
            p.add_argument("--actor", default="implementer")
        elif name == "event":
            p.add_argument("--kind", choices=("review", "test", "fix", "decision", "note"), default="note")
            p.add_argument("--text", required=True)
        elif name == "finish":
            p.add_argument("--assessment", choices=ASSESSMENTS, required=True)
            p.add_argument("--summary")
            p.add_argument("--input-tokens", type=int)
            p.add_argument("--output-tokens", type=int)
            p.add_argument("--token-source")
    args = parser.parse_args()
    try:
        project = project_root(args.project)
        if args.command == "start" and not args.task:
            raise ValueError("start requires --task (a short stable task description).")
        path, html, key = report_paths(project, args, create=args.command == "start")
        if args.command == "start":
            outcome = cmd_start(args, project, path, html, key)
        else:
            data = load(path)
            if data["identity"] != key:
                raise ValueError("Task identity mismatch.")
            if args.command == "finding":
                outcome = cmd_finding(args, data)
            elif args.command == "fix":
                outcome = cmd_fix(args, data)
            elif args.command == "event":
                outcome = cmd_event(args, data)
            elif args.command == "finish":
                outcome = cmd_finish(args, data)
            else:
                outcome = {"action": args.command, "rounds": len(data["sessions"]),
                           "findings": len(data["findings"])}
            if args.command not in ("show",):
                store(data, path, html)
        print(json.dumps({"task_key": key, "json": str(path), "html": str(html),
                          **outcome}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print("review_report: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
