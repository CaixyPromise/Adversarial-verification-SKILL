# Changelog

## 0.3.3 — 2026-11-02

- Review test cases for meaningful black-box assertions, negative/failure paths and complex multi-step business flows; do not accept happy-path-only tests for exposed material risks.
- Require explicit user confirmation before adopting, testing as an acceptance requirement, or implementing previously unspecified new business policy; keep established-contract defects actionable.
- Add optional behavioral-testing review reference without new agent roles, compulsory E2E suites, or new review gates.

## 0.3.2 — 2026-11-02

- Add optional atomic `av report import --file findings.json` batch ingestion for findings, fixes and review events, with whole-batch validation, stable finding references, duplicate-import protection and `--dry-run`.
- Document CLI commands and direct JSON fallback; reporting or file-write problems must not block coding, testing or Review delivery.

## 0.3.1 — 2026-11-02

- Add comprehensive [INSTALL.md](INSTALL.md) for Windows PowerShell, macOS and Linux, including fresh installs, upgrades, PATH, rollback, uninstall and troubleshooting.
- Support Windows `av.cmd` launchers through `av install-cli` without administrator rights, while preserving the Unix launcher and report CLI.
- Test Windows launcher generation, quote handling and existing-launcher protections; run CLI/report tests on both Linux and Windows CI runners.

## 0.3.0 — 2026-11-02

- Introduce `av` CLI that delegates to existing JSON/HTML review report commands without breaking task-level archive reuse.
- Add cached, bounded, nonblocking GitHub version checks; network errors do not block Review and only verified new versions are suggested.
- Support explicit `av check-update`, `av version` and opt-in `av update` with pinned SHA archive, safe extraction, backup and refusal to replace Git checkouts.
- Add CLI unit tests for pinned archive installation, Git checkout protection, safe archive extraction, task reuse, and local cache behavior; preserve executable modes during installation. No project code or reports are uploaded.

- Add cross-cutting artifact purity and minimal sufficiency: prevent AI discussion residue in user-facing text and code names, and avoid unnecessary flags/branches/wrappers created solely to demonstrate compliance. Keep genuine compatibility, safety and audit needs.

## 0.2.0 — 2026-11-01

- Add optional code structure and naming governance: evaluate cohesion, coupling, directory fragmentation and change locality; prevent AI conversation/temporary phase labels from leaking into filenames; avoid arbitrary LOC/file-count refactors.

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
