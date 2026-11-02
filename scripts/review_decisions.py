"""User confirmation/feedback records for local review dossiers.

These are separate from verified code defects and never change report assessments.
"""
from __future__ import annotations

from datetime import datetime
import re


KINDS = ("requirement-gap", "ambiguity", "tradeoff", "feedback")
STATES = ("pending", "resolved", "deferred")


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def validate_options(value):
    if not isinstance(value, list) or len(value) > 8:
        raise ValueError("Decision options must be an array with 0–8 items")
    result, ids = [], set()
    for choice in value:
        if not isinstance(choice, dict) or set(choice) - {"id", "text", "tradeoff"}:
            raise ValueError("Each option needs id, text and optional tradeoff")
        ident, text, tradeoff = choice.get("id"), choice.get("text"), choice.get("tradeoff", "")
        if (not isinstance(ident, str) or not ident.strip() or
                not isinstance(text, str) or not text.strip() or
                not isinstance(tradeoff, str) or ident in ids):
            raise ValueError("Invalid or duplicate decision option")
        result.append({"id": ident, "text": text, "tradeoff": tradeoff})
        ids.add(ident)
    return result


def add(data, session, *, title, kind="requirement-gap", context="", scenario="",
        evidence="", question="", options=None, recommendation="", blocking=False,
        linked_findings=None, decision_id=None):
    if not isinstance(title, str) or not title.strip() or kind not in KINDS:
        raise ValueError("Decision title or kind is invalid")
    for name, value in (("context", context), ("scenario", scenario), ("evidence", evidence),
                        ("question", question), ("recommendation", recommendation)):
        if not isinstance(value, str):
            raise ValueError("Decision " + name + " must be a string")
    if not isinstance(blocking, bool):
        raise ValueError("Decision blocking flag must be a boolean")
    options = validate_options(options if options is not None else [])
    links = linked_findings if linked_findings is not None else []
    if not isinstance(links, list) or any(not isinstance(x, str) for x in links):
        raise ValueError("Decision linked_findings must be an array of finding IDs")
    links = list(dict.fromkeys(links))
    known = {item["id"] for item in data.get("findings", [])}
    if any(x not in known for x in links):
        raise ValueError("Decision references an unknown finding")
    decisions = data.setdefault("decisions", [])
    if decision_id:
        found = next((d for d in decisions if d["id"] == decision_id), None)
        if found is None:
            raise ValueError("Unknown decision ID: " + decision_id)
    else:
        title_key = " ".join(title.casefold().split())
        found = next((d for d in decisions if d.get("kind") == kind and
                      " ".join(d["title"].casefold().split()) == title_key), None)
    if found and found.get("status") != "pending":
        raise ValueError("Decision already closed; do not silently reopen user-confirmed rules")
    fields = {
        "title": title.strip(), "kind": kind, "blocking": blocking,
        "context": context, "scenario": scenario, "evidence": evidence,
        "question": question or title.strip(), "options": options,
        "recommendation": recommendation, "linked_findings": links,
        "last_seen_round": session["round"]
    }
    if found:
        found.update(fields)
        action = "updated_decision"
    else:
        numbers = [int(d["id"][1:]) for d in decisions if re.fullmatch(r"D\d+", d["id"])]
        found = {
            "id": "D" + str(max(numbers or [0]) + 1).zfill(3),
            "status": "pending", "resolution": None, "history": [],
            "first_seen_round": session["round"], **fields
        }
        decisions.append(found)
        action = "created_decision"
    session["events"].append({
        "at": _now(), "kind": "decision",
        "text": found["id"] + ": " + action + " — " + found["title"]
    })
    return {"action": action, "decision_id": found["id"], "status": "pending"}


def resolve(data, session, *, decision_id, answer, source, status="resolved"):
    found = next((d for d in data.get("decisions", []) if d["id"] == decision_id), None)
    if found is None:
        raise ValueError("Unknown decision ID: " + decision_id)
    if found.get("status") != "pending":
        raise ValueError("Decision already closed; recorded resolution is immutable")
    if status not in ("resolved", "deferred"):
        raise ValueError("Decision status must be resolved or deferred")
    if (not isinstance(answer, str) or not answer.strip() or
            not isinstance(source, str) or not source.strip()):
        raise ValueError("Resolution requires an answer and confirmation source")
    record = {
        "status": status, "answer": answer.strip(), "source": source.strip(),
        "at": _now(), "round": session["round"]
    }
    found["status"] = status
    found["resolution"] = record
    found.setdefault("history", []).append(record.copy())
    session["events"].append({
        "at": _now(), "kind": "decision",
        "text": found["id"] + " → " + status + ": " + answer.strip()
    })
    return {"action": "resolved_decision" if status == "resolved" else "deferred_decision",
            "decision_id": found["id"], "status": status}
