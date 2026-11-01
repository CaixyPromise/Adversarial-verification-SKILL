# Changelog

## 0.2.0 — 2026-11-01

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
