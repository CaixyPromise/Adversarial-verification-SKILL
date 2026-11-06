# Review Playbook — Role-guided Engineering Review

Use only role sections and probes relevant to the change. These are **reasoning techniques**, not a ritual checklist. The risk score, 0–3 agent budget and stop criteria live in `SKILL.md`. For review completeness, batched repair and result wording, see `references/reasoning-convergence.md` when relevant. Use `references/project-conventions.md` for project-aware review; apply `references/engineering-quality.md`, `references/code-structure-governance.md`, `references/data-access-practices.md`, `references/frontend-experience.md`, `references/behavioral-testing.md` and `references/failure-attribution.md` **only when relevant**.

## Common method for every verifier

1. **Derive a provisional expected behavior and critical invariants independently** from the original requirement and trusted contracts, *before treating implementation notes as persuasive evidence*. Resolve ambiguities using real product and repository evidence; do not assume old code or tests are the specification.
2. Map the change to its **real execution/data path**, including relevant surrounding code, not just modified lines.
3. Form the strongest realistic **failure hypothesis**; inspect or probe it using safe, high-signal evidence. Inspect whether real black-box contract assertions and test fixtures would catch that failure.
4. Finish the **entire bounded assigned scope** before returning a consolidated report—not only the first or second defect. Supply inspected paths, business branches and meaningful test coverage plus outstanding gaps; do not hand off routine repairs mid-audit. Distinguish confirmed defects, design tradeoffs and unknowns.
5. Provide source locations, commands and observed results when actually executed. Never invent test runs, guarantees or business requirements.

## Agent A — Requirement & behavior correctness

**Question:** Did the change implement the *right* behavior, not simply a working behavior?

- Reconstruct concrete success criteria and the principal user/business journey from the request and existing product contracts.
- Walk **entry → authorization/validation → decision branches → state transitions → persistence/external effects → result**. Note where expected behavior may have been dropped or silently changed.
- Extract **business invariants** (e.g., ownership checks, unique financial effects, allowed transitions) and examine paths that could violate them.
- Probe at least the highest-risk alternative branch or failure path when applicable: invalid state, missing/duplicate input, retries, partial completion.
- Inspect the **test cases** and actual outputs against intended semantics; challenge happy-path-only fixtures, implementation-mirroring mocks and weak assertions. Select black-box negative paths and multi-step business chains for high-risk cases; check final state, side effects and invariants, not just a successful call.
- When a material rule admits multiple valid interpretations and evidence cannot resolve it, provide the exact **human decision required**; never quietly impose a preference. Do not promote a newly imagined rule outside the approved scope into an acceptance test or implementation before the user explicitly confirms; report it as a proposal instead.

**Deliver:** specific entry paths/branches/tests covered and missing material scenarios, observed versus expected behavior, all proven scoped findings in one batch, violated invariants and unresolved product decisions.

## Agent B — Implementation consistency & pragmatic reuse

**Question:** Does the new code fit established implementation and business semantics without unnecessary duplication or premature abstraction?

### Bounded search: expand only when evidence warrants it

1. **Changed module:** inspect related functions, services, adapters, tests and local helpers.
2. **Direct callers/dependencies:** follow affected contracts, shared data models and nearby similar behavior.
3. **Relevant shared code:** search for an existing suitable utility, domain service, policy or library; avoid unrestricted repository-wide exploration unless a concrete cross-module concern justifies it.
4. **Selective history:** use relevant `git log`, `git blame` or prior fixes only when the design rationale, compatibility or a regression cannot be explained by current code. History is evidence, **not authority**.

**Stop expanding the search** when enough evidence exists to assess behavioral consistency and choose a reasonable reuse direction. Do not repeatedly mine history for speculative refactoring opportunities.

### Compare semantics before recommending reuse

Compare input/output contracts, validation, error behavior, authorization, domain ownership, state transitions, side effects, transaction boundaries, lifecycle and change expectations. Similar names or code shape **do not** imply equivalent behavior. Conversely, different implementations of the same business rule may indicate harmful drift.

### Progressive reuse and extraction

Prefer the **smallest sound design** supported by real reuse or maintenance evidence:

| Evidence | Preferred direction |
| --- | --- |
| Existing implementation already provides the **same semantics** | **Reuse directly**, preserving its contract and ownership |
| Repeated stable logic **inside one module** | Consider a module-local helper/service or extraction, if it reduces actual maintenance cost |
| Stable **technical utility** repeatedly needed by independent modules | Consider a shared utility/package with clear ownership, dependency direction, tests and version/compatibility expectations |
| Duplicated **business decision** across callers | Consider a shared **domain service/policy** owned by the relevant domain, not a generic `Utils` bucket |
| Superficially similar implementations with distinct rules, evolution or ownership | **Keep separate**; favor simple local code over coupling |

No fixed duplicate count mandates extraction. Several recurring independent uses, repeated fixes, divergence or measurable maintenance burden are **signals**, not automatic triggers. If a repository has no common utility package, **do not create one merely for one or two helpers**; propose a focused shared package only when recurring cross-module usage and stable semantics justify its cost. Avoid dumping unrelated functions into one global utility module or creating dependency cycles.

An optional refactor must not silently expand the user's requested change. Report non-blocking reuse opportunities separately unless duplication causes a **demonstrable correctness, compatibility or material maintenance failure**.

**Useful evidence:** targeted symbol/reference searches, call/data flow, comparable implementations, existing tests and selective read-only history. If history is unavailable, use current code and disclose the limit.

**Deliver:** relevant changed code and direct callers/dependencies inspected, behavioral/contract consistency, all confirmed scoped defects in one batch, justified reuse suggestions and material unreviewed gaps.

## Agent C — System-level engineering risk

**Question:** Could the change fail under real workloads, hostile access, historical system constraints or distributed execution?

- Identify the relevant **trust, process, network, persistence and deployment boundaries**. Focus on what this change actually touches.
- **Attribution:** before fixing a failing test, distinguish a project-owned misuse/integration regression from upstream browser/library defects, environment or CI setup, and unknown causes. Check versions/contracts and bounded diagnostics; never reflexively install another browser or driver. See `references/failure-attribution.md`.
- **Security:** identity origin, authorization/ownership enforcement, untrusted input, secrets and failure-denial semantics; hidden UI controls are not server authorization.
- **Performance & resources:** critical paths, query shape/N+1, repeated expensive work, allocations, caches, connections, event listeners, worker cleanup and input growth.
- **Concurrency & distributed systems when relevant:** atomicity, duplicate delivery, idempotency, ordering, locks, races, retries/timeouts, partial failures, compensation, restart recovery, backpressure and eventual consistency guarantees.
- **Historical maintainability & compatibility:** prior incidents or known fragile paths when accessible, legacy callers, schema/version upgrades, rolling deployments, configuration drift, logging/metrics, observability and rollback.
- Choose **one or more high-signal probes** only for material risks: an unauthorized access, a duplicate concurrent mutation, a failed dependency, an old-data migration, a realistic workload comparison, or a restart/reconnect scenario.
- Separate measured effects from plausible hypotheses; do not invent scalability, distributed or security concerns when not relevant. State attribution confidence and disclose blocked external verification rather than guessing fault ownership.

**Deliver:** all material scoped failure modes and their evidence (security, persistence, concurrency, performance and upstream ownership as applicable), inspected paths/probes, residual unverified risks; do not end upon the first failing test.

## Selective techniques (not mandatory for each role)

- **Change-impact analysis:** symbol search, call/data-flow trace, API/schema diff and affected neighboring tests.
- **Invariants/state-machine reasoning:** legal/illegal transitions, repeated actions, ownership, failure paths and side effects.
- **Fault/concurrency probes:** controlled timeouts, retry duplicates, partial writes, cancellation and restart; avoid production side effects.
- **Test effectiveness:** black-box observable results, realistic fixtures, negative cases and multi-step integration scenarios when risk warrants; property-based tests, targeted mutation or fuzzing are optional. Tests must guard approved behavior, not define unapproved policy. See `references/behavioral-testing.md`.
- **Design review:** inspect abstraction boundaries, coupling, repeated business decisions, contract stability and complexity, while avoiding speculative refactors.
- **Operational validation:** realistic workload, controlled environment, deployment/rollback compatibility and diagnostics where relevant.

Do not automatically run every build, test suite or category for every task. Use the cheapest **reliable falsification** of the material risks; document skipped high-impact coverage.

## Change attribution — compare against the baseline

Before classifying a discovered problem as a new regression, use the cheapest credible comparison: relevant `git diff` / base commit code, existing equivalent paths, or the same focused test/behavior before and after the change **when safe and feasible**.

- **Introduced:** present only after the change → prioritize as a review finding.
- **Worsened:** an existing issue becomes materially worse because of the change → identify the new impact and scope.
- **Pre-existing:** observable before the change → separate unrelated technical debt from issues that directly block the requested outcome. Critical old security/data risks still merit prompt escalation.
- **Unknown:** no reliable baseline or enough evidence → label uncertainty; do not assert change causation.

Do **not** turn an unrelated historic defect into a required refactor for the current task. Do not ignore a previously existing defect if it defeats the requested feature or a necessary safety boundary. Keep the evaluation focused on the actual change.

## Cross-agent synthesis and targeted re-verification

When multiple reviewers find the same root cause, **merge** their evidence rather than counting two bugs. When they disagree, trace the requirement and code path; the parent arbitrates with evidence, not votes. Parent verifies that A/B/C relevant scopes were covered even when only one or two reviewers were assigned.

Report each blocking finding as **violated requirement/invariant → trigger/code path → expected/actual evidence → change attribution → impact → smallest sound repair**. Keep improvements and unverified possibilities separate. After the parent batches fixes by shared root cause, rerun the relevant failure probes plus affected regression paths. A new issue on an **unchanged path already within the original scope** is a first-review coverage miss, not normal incremental discovery; close that scope gap coherently before another repair batch. Do not force all reviewers to repeat a complete review merely to change the final assessment.
