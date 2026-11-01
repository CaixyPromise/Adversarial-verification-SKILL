# Changelog

## 0.2.0 — 2026-11-01

- Add optional project, data-access/cache and frontend-experience review references, grounded in project and official framework conventions.
- Ensure final UI titles, subtitles and labels communicate product functionality rather than rejected conversation-specific implementation alternatives; preserve necessary factual/audit records.

- Add optional `references/engineering-quality.md`: sourced engineering-quality criteria for correctness, architecture, reuse, testing, security, reliability, performance, and operability; explicitly reject checklist-driven PASS chasing and unsupported style blockers.

- Reopen previously resolved findings without creating new IDs or losing repair history.
- Require explicit token provenance when recording actual usage, and reject negative counts.
- Add an optional offline review dossier: one reusable JSON + interactive static HTML per task across multiple rounds, with evidence, proposals, applied fixes, re-verification, timestamp provenance and optional measured tokens.
- Protect archives from Git tracking through local info/exclude, reuse existing skill archive directories, and provide a dependency-free Python generator.

- Make requirements, business flows and invariants the source of review truth.
- Define complementary reviewer roles: A requirement correctness, B current/historical implementation consistency with pragmatic reuse, C system-level security/performance/maintenance/distributed risks.
- Add role-specific investigation methods and coverage merging for 0/1/2/3 verifier allocations.
- Require independent expected-behavior reasoning before trusting implementation summaries.
- Add baseline comparison and change attribution: introduced / worsened / pre-existing / unknown, with separate treatment of unrelated historical risks.
- Prevent business ambiguity from inflating agent count; resolve material rules before scaling reviewers.
- Bound implementation-consistency searches and introduce evidence-driven reuse: existing utility → module-local extraction → cross-module shared utility, while keeping domain rules in domain services/policies.
- Add 0–6 risk scoring and adaptive **0–3 verifier subagent** allocation (three maximum, never a quota).
- Replace indefinite FAIL/review loops with one coverage-first round, targeted re-verification and explicit stopping conditions.
- Distinguish evidence-backed blockers, improvements and unverified risks; introduce READY / CHANGES_NEEDED / NEEDS_DECISION / PARTIAL delivery assessments.
- Consolidate duplicated verifier templates, playbooks and parent repair policies.
- Correct root-directory installation instructions and remove machine-specific paths.
- Breaking change: integrations parsing legacy PASS/FAIL/PARTIAL verdict lines must migrate.

## 0.1.0

Initial open-source packaging of `adversarial-verification` with independent verifier prompts, parent/repair policies, domain checklists and bilingual documentation.
