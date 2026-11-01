---
name: adversarial-verification
description: Requirement-driven, risk-adaptive verification of coding changes. Use for independent code review, adversarial checks, regression analysis, business-flow validation, and evidence-based delivery assessment. Allocate zero to three verifier subagents based on complexity, impact, and uncertainty; do not require a verifier for trivial changes.
---

# Adversarial Verification

## Purpose

Protect **intended business behavior** with proportionate, evidence-based review. The goal is **not** to maximize findings, repeatedly obtain PASS, or prove code defect-free. Review what the user actually requested and what the change can break.

The implementing (parent) agent owns delivery and decisions; independent verifier subagents inspect and test but do not edit implementation files. A review is a decision aid, not release authorization.

## 1. Understand before judging

Derive a short review brief from the original request, acceptance criteria, project conventions, relevant code/tests, and the actual diff:

- **Intent:** What observable outcome should the user get?
- **Invariants:** Which business rules, authorization boundaries, data properties, or compatibility contracts must remain true?
- **Flow:** Which entry points, decisions, state transitions, side effects, and upstream/downstream paths are affected?
- **Unknowns:** Which assumptions could change whether the implementation is correct?

Do not treat existing tests, the implementation summary, or the current code behavior as the specification. Independently verify important assumptions against sources. Inspect relevant existing implementations (and historical changes when useful) to understand established contracts and why designs evolved; **history is evidence, not an unquestionable requirement**.

Resolve ordinary uncertainty from available evidence. **Ask the human before deciding** only when a material product/business rule cannot be established and different interpretations change the implementation or review outcome. State the exact decision and plausible alternatives. Do not invent a rule or endlessly interrogate the user.

**Uncertainty is not solved by adding reviewers.** When unresolved business ambiguity would change the expected behavior or verdict, first narrow it using repository/product evidence, then request the minimal human decision if still material. Do not escalate agent count *solely* because the uncertainty score is high; assess independent technical risk after identifying the ambiguity.

## 2. Assess risk and allocate agents

Score each axis **0–2**, based on the change and its context:

| Axis | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Complexity | Cosmetic / isolated | One module / modest state | Cross-module, concurrent, distributed or complex state |
| Impact | Negligible | Local feature or user-facing regression | Core flow, auth/security, data integrity, financial or hard-to-reverse impact |
| Uncertainty | Clear behavior | Minor assumptions | Materially ambiguous requirement or contract |

Total **0–6**; this is a heuristic, not a proof of risk.

| Score | Default independent verifier subagents | Review |
| --- | --- | --- |
| 0–1 | **0** | Implementer checks the direct result; skip independent review |
| 2–3 | **1** | Focused review of requirements and likely regressions |
| 4–5 | **2** | Separate business/flow and highest-risk technical concerns |
| 6 | **3** | Independent, complementary high-risk perspectives |

**Maximum: 3 verifier subagents per review round.** Counts refer to verifier subagents; the parent agent is not an extra verifier. Use fewer when scopes cannot be meaningfully separated, resources are unavailable, or the change does not justify them. At score 4–5, a third verifier is allowed only for a clearly distinct material risk. Critical security, authorization, financial, privacy, or irreversible-data changes require elevated scrutiny even if few lines change; typically at least two complementary reviews when subagents are available.

### Distinct reviewer responsibilities

For substantial changes, divide review into **three complementary lenses**, not three copies of the same review:

- **Agent A — Requirement & behavior correctness:** Independently reconstruct user intent, acceptance criteria, business flow and invariants. Trace entry points, decisions, state changes and external effects. Find omitted requirements, incorrect semantics and invalid state transitions. Do not infer product rules solely from the new implementation.
- **Agent B — Implementation consistency & pragmatic reuse:** Trace changed symbols beyond the diff; compare similar **current and prior implementations**, shared utilities, established contracts and relevant Git history when useful. Search progressively: **changed module → direct callers/dependencies → relevant shared code → selective history**; stop once evidence is sufficient. Detect duplicated *business rules* as well as code, semantic divergence, avoidable parallel paths, and incompatible integration patterns. Prefer existing compatible utilities, then module-local extraction; consider a shared utility package only for repeatedly needed, stable, genuinely cross-module technical behavior. Keep business rules in their owning domain service/policy rather than generic utilities. **Prefer reuse only where semantics, ownership, dependency direction and evolution align; never abstract or consolidate for its own sake.** Historical code may contain obsolete decisions or defects.
- **Agent C — System-level engineering risk:** Trace the change through technical boundaries and production assumptions. Inspect relevant security and authorization, performance/scalability, resource lifecycle, long-term maintenance, compatibility, and—when applicable—distributed concurrency, retries, idempotency, partial failures, data consistency and recovery. Test the **highest-risk failure mechanisms**, not every conceivable category.

**Assignment when fewer than three verifiers are warranted:**
- **0:** Parent checks the direct outcome; do not invent subagent work.
- **1:** One verifier covers A + B + C **proportionately**, emphasizing material risk.
- **2:** Assign A and a combined B + C reviewer by default; split B versus C differently if one dominates. Parent checks that no material lens was omitted.
- **3:** Assign A, B and C separately. Each gets a distinct scope and produces independent findings.

These are review lenses, **not fixed agent classes or compulsory checklists**. Avoid redundant code reading; when relevant, agents may share pointers to evidence while reaching independent conclusions. Every verifier receives the original request, relevant requirements/invariants, changed code and assigned role(s), **without** the implementer's confidence or preferred verdict.

Use this concise dispatch contract rather than separate specialized prompt templates:

```text
Review role(s): [A / B / C and concrete focus]
Original user request and acceptance criteria: [...]
Known business invariants and unknowns: [...]
Changed paths and implementation summary: [...]
Relevant repository instructions and safe verification commands: [...]
Deliver: scoped coverage, evidence-backed blocking defects,
non-blocking improvements, unverified risks, and verification limits.
Independently inspect applicable surrounding code/history; do not edit.
```

For concrete investigation tactics, read your assigned role section in `references/review-playbook.md`.

If subagents are not available, do a scoped self-review and disclose the lack of independent verification.

## 3. Conduct one coverage-first review

Inspect the actual changed behavior and its meaningful blast radius **before** finalizing findings. Start with requirement and flow correctness; then selectively check:

- **A:** missing or distorted requirements, incorrect business flow, violated invariants and acceptance criteria
- **B:** existing and earlier equivalent implementations, bounded searches for suitable reuse, duplicated or diverging business rules, sensible local/shared extraction, compatibility with established module contracts
- **C:** relevant security, data integrity, performance, concurrency/distributed failure, resource lifecycle, upgrade compatibility and production maintainability risks
- across roles: callers, callees, neighboring regressions, invalid states, boundary inputs, error paths, and **whether tests could detect the actual defect**

Use the most informative feasible evidence: code-path analysis, focused tests, direct execution, runtime outputs/logs, or relevant existing test suites. A direct run is strongly preferred for executable behavioral changes but not mandatory for documentation/config-only changes or unsafe environments. Do not treat green tests, HTTP 200, or exit status 0 as sufficient evidence of business correctness.

**Do not stop at the first one or two bugs.** Finish each assigned material risk area, combine subagent results, remove duplicates, challenge weak findings and report one coherent set. In particular, **compare implementation consistency against existing patterns before recommending new abstractions or duplicate logic**. The parent reconciles disagreements using requirements and evidence, not majority voting. Aim for sufficient coverage, not an impossible guarantee of finding every bug. State meaningful gaps.

Read `references/review-playbook.md` only for relevant probing tactics. For security-sensitive changes, also use `references/security-review-checklist.md`.

## 4. Findings and severity

Report a blocking defect only with:

- the violated requirement, invariant or justified safety property
- trigger/preconditions and a concrete code path or reproduced observation
- expected versus actual behavior and practical impact
- minimal recommended repair direction

For executed checks, give commands and observed results. For code-only analysis, give specific locations and reasoning, **not fabricated execution evidence**.

Group results as **Blocking defects**, **Non-blocking improvements**, and **Unverified risks/assumptions**. Style preferences, speculative vulnerabilities, or unproven hypotheticals are not blockers. Confirmed critical/high security issues and material business/integrity failures are blockers. State uncertainty instead of inventing certainty.

## 5. Repair, reverify, and stop

The parent validates findings, fixes confirmed defects at their **business/engineering root cause**, and does not game fixtures, weaken contracts, swallow errors, or silently alter product policy.

Run **one broad review round** with applicable independent scopes. After changes, **targeted re-verification** must cover each repaired issue and affected regression paths; do not restart the entire review by default. Re-scope only if the repair materially expands the change or reveals a new independent high-risk area.

**Stop** when sufficient applicable coverage is complete and no known blockers remain; when a human decision or environment prevents necessary verification; or when the same blocker has survived **two unsuccessful repair-and-reverify cycles**. In the latter cases, report the blocker, evidence, attempts and what would unblock it. Never keep looping merely to obtain a success label. An unresolved blocker must not be described as ready.

Use exactly one delivery assessment:

- `READY` — required evidence is sufficient; no known blockers within reviewed scope (not proof of bug-free code).
- `CHANGES_NEEDED` — confirmed blocking defects remain.
- `NEEDS_DECISION` — a material business/product decision blocks a sound conclusion.
- `PARTIAL` — necessary verification is unavailable or incomplete; describe what is and is not supported.

Finish concisely with: **requirement/flow understood, risk score and role-based verifier allocation, coverage of A/B/C as applicable, findings with evidence, residual risks, final assessment**. No artificial PASS quotas or repeated full-review gates.

## Safety boundaries

Verifier subagents are read-only with respect to repository implementation files: no edits, dependency installation or Git write operations. Scratch probes may be placed under temporary directories. Use controlled environments; never run destructive, externally billable, production-data-modifying or otherwise irreversible probes without explicit authorization. If safe direct execution is impossible, use static evidence and disclose the gap.
