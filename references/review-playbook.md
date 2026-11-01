# Review Playbook — Role-guided Engineering Review

Use only the role sections and probes relevant to the change. These are **reasoning techniques**, not a ritual checklist. The authoritative risk score, 0–3 agent budget, safety rules, reporting and stop criteria live in `SKILL.md`.

## Common method for every verifier

1. Establish the **expected behavior** from the original requirement, business rules and trusted contracts; do not copy the implementer's conclusion.
2. Map the change to its **real execution/data path**, including relevant surrounding code, not just modified lines.
3. Form the strongest realistic **failure hypothesis**; inspect or probe it using safe, high-signal evidence.
4. Finish the **relevant coverage** before delivering a consolidated report. Distinguish confirmed defects, design tradeoffs and unknowns.
5. Provide source locations, commands and observed results when actually executed. Never invent test runs, guarantees or business requirements.

## Agent A — Requirement & behavior correctness

**Question:** Did the change implement the *right* behavior, not simply a working behavior?

- Reconstruct concrete success criteria and the principal user/business journey from the request and existing product contracts.
- Walk **entry → authorization/validation → decision branches → state transitions → persistence/external effects → result**. Note where expected behavior may have been dropped or silently changed.
- Extract **business invariants** (e.g., ownership checks, unique financial effects, allowed transitions) and examine paths that could violate them.
- Probe at least the highest-risk alternative branch or failure path when applicable: invalid state, missing/duplicate input, retries, partial completion.
- Compare tests and actual outputs to the intended semantics; ask whether a wrong implementation could still pass.
- When a material rule admits multiple valid interpretations and evidence cannot resolve it, provide the exact **human decision required**; never quietly impose a preference.

**Deliver:** requirement coverage, observed behavior versus intended behavior, missing cases, violated invariants, unresolved product decisions.

## Agent B — Implementation consistency & pragmatic reuse

**Question:** Does this implementation fit the *actual* codebase, including prior solutions and established business semantics?

1. Start at the changed symbols/interfaces. Follow relevant callers, callees, data models, contracts and tests.
2. Search **current repository implementations** of the same or analogous behavior, including common helpers, domain services, policies, adapters and error handling. Look for duplicated **business decisions** as well as repeated code.
3. When a relevant design is unclear or has evolved, selectively inspect **Git history / blame / prior fixes** (read-only, if available); do not exhaustively mine history for a trivial diff.
4. Compare **semantic equivalence**, not names or syntax: input conditions, outputs, authorization, ownership, side effects, transactional boundaries, error rules and lifecycle. Ask whether the new path changes a rule that existing paths still rely on.
5. Recommend reuse **only when** the existing abstraction really represents the same concept, its owner and dependency direction are appropriate, and expected evolution is aligned. Prefer minimal local code when shared abstraction would introduce coupling or conceal distinct domain semantics.
6. Check that integrations and tests preserve established contracts. Identify accidental parallel implementations, drift and needless complexity, but **do not fail a change for cosmetic differences or simple duplication alone**.

**Useful evidence:** repository-wide symbol references, comparable code paths, existing tests, call graphs where available, `git log`/`git blame` for relevant context. A historical implementation is **not automatically correct**, and an old pattern may have been deliberately replaced. If history is unavailable, review current code and state that limitation.

**Deliver:** consistency/compatibility findings, proven duplicated/diverging business logic, justified reuse opportunity versus deliberate separation, evidence and maintenance impact.

## Agent C — System-level engineering risk

**Question:** Could the change fail under real workloads, hostile access, historical system constraints or distributed execution?

- Identify the relevant **trust, process, network, persistence and deployment boundaries**. Focus on what this change actually touches.
- **Security:** identity origin, authorization/ownership enforcement, untrusted input, secrets and failure-denial semantics; hidden UI controls are not server authorization.
- **Performance & resources:** critical paths, query shape/N+1, repeated expensive work, allocations, caches, connections, event listeners, worker cleanup and input growth.
- **Concurrency & distributed systems when relevant:** atomicity, duplicate delivery, idempotency, ordering, locks, races, retries/timeouts, partial failures, compensation, restart recovery, backpressure and eventual consistency guarantees.
- **Historical maintainability & compatibility:** prior incidents or known fragile paths when accessible, legacy callers, schema/version upgrades, rolling deployments, configuration drift, logging/metrics, observability and rollback.
- Choose **one or more high-signal probes** only for material risks: an unauthorized access, a duplicate concurrent mutation, a failed dependency, an old-data migration, a realistic workload comparison, or a restart/reconnect scenario.
- Separate measured effects from plausible hypotheses; do not invent scalability, distributed or security concerns when not relevant.

**Deliver:** concrete failure modes, triggering conditions, estimated impact and scope, directly observed or code-backed evidence, residual untested risks.

## Selective techniques (not mandatory for each role)

- **Change-impact analysis:** symbol search, call/data-flow trace, API/schema diff and affected neighboring tests.
- **Invariants/state-machine reasoning:** legal/illegal transitions, repeated actions, ownership, failure paths and side effects.
- **Fault/concurrency probes:** controlled timeouts, retry duplicates, partial writes, cancellation and restart; avoid production side effects.
- **Test effectiveness:** negative tests, property-based tests, a *targeted* mutation experiment or fuzzing when cost and input surface justify them. Passing tests alone do not prove that incorrect behavior would be caught.
- **Design review:** inspect abstraction boundaries, coupling, repeated business decisions, contract stability and complexity, while avoiding speculative refactors.
- **Operational validation:** realistic workload, controlled environment, deployment/rollback compatibility and diagnostics where relevant.

Do not automatically run every build, test suite or category for every task. Use the cheapest **reliable falsification** of the material risks; document skipped high-impact coverage.

## Cross-agent synthesis and targeted re-verification

When multiple reviewers find the same root cause, **merge** their evidence rather than counting two bugs. When they disagree, trace the requirement and code path; the parent arbitrates with evidence, not votes. Parent verifies that A/B/C relevant scopes were covered even when only one or two reviewers were assigned.

Report each blocking finding as **violated requirement/invariant → trigger/code path → expected/actual evidence → impact → smallest sound repair**. Keep improvements and unverified possibilities separate. After repair, rerun the relevant failure probe plus the affected regression paths. Do not force all reviewers to repeat a complete review merely to change the final assessment.
