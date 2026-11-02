# Adversarial Verification

A lightweight, **requirement-driven and risk-adaptive** code-review skill for AI coding agents.

It reviews whether an implementation meets the **actual user intent**, preserves business invariants, and avoids material regressions. Independent adversarial verification remains available, but is **not a compulsory ritual** for trivial changes. Findings and evidence matter more than obtaining a PASS label.

中文说明：[README_zh.md](./README_zh.md)

## How it works

1. **Understand:** determine intended behavior, key business flow, invariants and material unknowns from the user request and codebase.
2. **Assess:** score complexity, impact and uncertainty, 0–2 each; total 0–6.
3. **Review:** cover requirements, affected paths, regressions and relevant technical risks in one broad round.
4. **Resolve:** address proven blockers at their root cause and ask a human for material unresolved business decisions.
5. **Finish:** targeted re-verification, explicit coverage and residual risks; no indefinite PASS-chasing loop.

## Review budget: up to three verifier subagents

| Risk score | Default verifier subagents | Typical use |
| --- | --- | --- |
| 0–1 | 0 | Cosmetic or isolated, directly check the result |
| 2–3 | 1 | Focused feature/behavior check |
| 4–5 | 2 | Business flow and a distinct technical risk |
| 6 | 3 | Complementary business, safety/state and regression perspectives |

A third verifier is also allowed for a 4–5 score when a distinct material risk justifies it. **Three is a cap, not a quota**; do not assign multiple agents the same question. Serious security/authorization, data-integrity, financial or irreversible operations receive elevated scrutiny even for short diffs. If business rules are materially unclear, resolve them from evidence or ask for a decision before multiplying reviewers; ambiguity alone does not justify more agents.

### Reviewer roles and how they review

- **A — Requirement correctness:** independently derive acceptance criteria and business invariants, trace the full intended journey and find semantic mistakes or missing scenarios.
- **B — Implementation consistency:** search progressively (changed module → direct dependencies → relevant shared code → selective history), compare existing business semantics and file/module cohesion, coupling, fragmentation and stable names where relevant, and prefer existing reuse or module-local extraction. A shared utility package is appropriate only when stable cross-module technical behavior recurs; shared business rules belong in domain services/policies. **Never abstract merely because code looks similar.**
- **C — System engineering:** assess applicable performance, security, long-term maintenance, system compatibility and distributed failure/concurrency risks using targeted probes.

With **one** reviewer, cover all three lenses in proportion to risk. With **two**, default to A and combined B+C (or split differently for the dominant risk); parent checks gaps. With **three**, assign A/B/C separately. Role-specific investigation guidance is in `references/review-playbook.md`. No role is a reason to demand refactoring purely for reuse.

## Result format

- `READY`: applicable coverage sufficient, no known blockers in reviewed scope.
- `CHANGES_NEEDED`: verified blocking defects remain.
- `NEEDS_DECISION`: a material business/product decision is missing.
- `PARTIAL`: required evidence or verification environment is unavailable.

These are **delivery assessments**, not mathematical claims of correctness or production approval. Reviewers **independently derive expected behavior** from the request and trusted contracts before accepting the implementer's rationale. Where feasible, compare baseline and changed behavior and label findings **introduced / worsened / pre-existing / unknown**. Keep unrelated existing problems out of the current repair scope while escalating serious historical safety issues. Every blocking finding needs a specific violated rule, trigger, code/runtime evidence, impact, and repair direction. Improvements and open hypotheses are separate.

One broad review round is the default. Fixes receive targeted re-verification of the issue and affected paths. After two unsuccessful repair cycles for the same blocker, stop automatic looping and escalate with evidence.

## Optional local review dossier

For review evidence, costs and repair history, use the standard-library helper `scripts/review_report.py` (see [reporting guide](references/reporting.md)). It generates **one reusable JSON and static interactive HTML pair per task**. Reviewers submit proposals; the implementer records actual fixes and verification; subsequent review rounds update the same dossier. The HTML supports filtering, expand/collapse, per-round history, printing and JSON export without a web server. Timing is measured only between recorded invocations; token figures appear only when supplied by trustworthy telemetry. Reports stay local and are protected with `.git/info/exclude` rather than committed.

## CLI — Review reports and Skill updates

Python 3.9+ standard library only. After installation, run from the Skill directory:

```bash
python3 scripts/av.py install-cli   # creates a small launcher in ~/.local/bin
av version
av report start --task-id ISSUE-123 --task "Permission clone" --risk 5 --agents 2
av report finding --task-id ISSUE-123 --title "Missing owner validation" --evidence "Service path permits a cross-user write" --proposal "Validate ownership in service"
av report finish --task-id ISSUE-123 --assessment CHANGES_NEEDED

av check-update       # explicit, immediate GitHub version lookup
av update             # asks before replacing a non-Git installed Skill
av update --yes       # explicit non-interactive confirmation
```

If the launcher directory is not on `PATH`, call `python3 /path/to/skill/scripts/av.py` instead. For a different project, provide `--project /path/to/project` **before** `report`. The older `scripts/review_report.py` interface remains supported. On Windows use Python to run the script directly.

**Nonblocking version discovery:** ordinary report CLI calls show any cached update notice and, at most once every 24 hours, launch a detached, time-limited version metadata check. The result is cached under `~/.cache/adversarial-verification/update-check.json` (or `$XDG_CACHE_HOME`); the first call may only show the notice on the next invocation. GitHub outages never block reporting. Disable this network check with `AV_DISABLE_UPDATE_CHECK=1`. No project code, report contents or telemetry are uploaded.

**Updating is opt-in:** `av update` fetches the official GitHub main commit, checks a pinned version manifest, downloads that exact GitHub archive via HTTPS, rejects unsafe archive paths/links, stages the replacement and keeps the old Skill in a sibling backup folder. It refuses to overwrite Git working trees (use `git pull` there). Existing project review archives are unaffected. Restart your coding agent after updating.

**Artifact purity:** avoid final UI copy, filenames or unnecessary mechanisms that merely narrate rejected AI-user discussion alternatives. Preserve genuine compatibility, security and audit requirements.

## Files

- `SKILL.md` — authoritative workflow and 0–3 agent allocation.
- `references/review-playbook.md` — role-specific investigation methods and optional engineering probes.
- `references/engineering-quality.md` — evidence-based engineering-quality principles.
- `references/project-conventions.md` — applicable repository/agent instructions, language and toolchain constraints.
- `references/code-structure-governance.md` — responsibility-based file splitting/consolidation, directory cohesion, change locality, durable names and safe refactoring checks.
- `references/data-access-practices.md` — N+1, indexes, transactions, deadlocks, cache consistency.
- `references/frontend-experience.md` — theme/component reuse, plain-language UX and no leaked conversation notes in UI.
- `references/security-review-checklist.md` — optional security guidance.
- `agents/openai.yaml` — skill interface metadata.
- `scripts/av.py` and `skill-version.json` — CLI, cached GitHub update checks and explicit verified Skill updater.
- `scripts/review_report.py` and `templates/review-report.html` — backwards-compatible offline dossier generator and static report template.
- `references/reporting.md` — usage, archive discovery, provenance and Git safety.

## Installation (Windows / macOS / Linux)

See **[INSTALL.md](INSTALL.md)** for the complete guide: PowerShell installation on Windows 10/11, `av.cmd` launcher and user PATH setup, macOS/Linux installation, previous-version upgrades, Git-clone workflow, rollback and troubleshooting.

**Quick start:** install Python 3.9+ and place this repository's root contents in your Codex skill folder (`~/.codex/skills/adversarial-verification`). Then run `python3 scripts/av.py install-cli` on macOS/Linux, or `py -3 scripts/av.py install-cli` on Windows from the installed Skill folder. Windows creates `~/.local/bin/av.cmd`, Unix creates `~/.local/bin/av`.

`av version` displays the installed version; `av check-update` checks GitHub; `av update` asks for confirmation before replacing an archive-installed Skill. Git checkouts must update through Git. Review reports stay in the reviewed project, not in the Skill directory.

## Migration from v0.1

The old `PASS/FAIL/PARTIAL` contract and 11 category-specific prompt templates have been replaced by a requirement-first decision and a compact on-demand playbook. **Update any integrations parsing the old verdict strings.** The original independent, read-only verifier concept and root-cause repair policy remain.

## License

MIT.
