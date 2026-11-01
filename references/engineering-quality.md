# Engineering Quality — Evidence-Based Review Reference

> **Use selectively, not as a compulsory gate.** For project-specific context see `project-conventions.md`; for structure and naming see `code-structure-governance.md`; for changed data/cache paths see `data-access-practices.md`; for frontend changes see `frontend-experience.md`. This guide defines *how to judge* whether a change is good engineering. The original user requirements, domain invariants, repository conventions and actual operational constraints take precedence. It supports the A/B/C reviewers in `SKILL.md`, without adding agents, a new score, a review round or mandatory artifact.

## Quality standard and decision rule

A good change **solves the requested problem correctly**, preserves important contracts and safety properties, and is **no more complex than justified**, while leaving the relevant codebase understandable, testable and operable.

Review should improve overall code health **without blocking useful delivery for hypothetical perfection**. Avoid applying every item to every change. Focus on risks exposed by the diff and its affected execution paths.

For a quality concern, the reviewer should be able to state:

1. **Context:** Which requirement, invariant, established contract or runtime constraint applies?
2. **Mechanism:** Which actual code path, dependency, state transition or production assumption violates it?
3. **Consequence:** What breaks for users, operators or future maintainers, and under which conditions?
4. **Evidence and response:** What observation, comparison, test or concrete code reasoning supports the claim? What is the **smallest sound correction**?

No demonstrated material impact => **non-blocking improvement**, question or explicit uncertainty; never invent a defect merely to fill a checklist. A confirmed critical security, authorization or integrity violation remains blocking even if old or outside the immediate diff; attribute it correctly and escalate separately when appropriate.

## Review lenses and practical standards

| Quality area | What **good** looks like | High-signal probes and warning signs | Primary role |
| --- | --- | --- | --- |
| **Requirement & behavioral correctness** | Observable acceptance criteria and business invariants hold across the relevant user journey | Trace real input → branching → state → side effects; check omitted cases, invalid transitions and incorrect authorization decisions | A |
| **Module & API boundaries** | Responsibilities are clear; interfaces and error contracts are stable; dependencies follow the codebase's ownership rules | Follow callers/callees; inspect API/schema compatibility, hidden cross-layer calls, accidental shared mutable state | B |
| **Simplicity & justified reuse** | Smallest implementation consistent with existing architecture; shared logic reflects truly shared semantics | Compare existing utilities/implementations; watch duplicate business rules, speculative generalization, excessive wrappers or circular dependencies | B |
| **Test effectiveness** | Tests detect meaningful wrong behavior with maintainable assertions and appropriate test scope | Ask "would this test fail if an authorization/condition branch were inverted?"; check changed contract, negative cases, integration seams, brittle mocks | A + B |
| **Security & data integrity** | Trust boundaries enforce identity, permissions, validation and consistency in the appropriate layer | Targeted unauthorized/cross-tenant attempts, injection paths, atomicity, secret exposure, unsafe fallbacks; consult the security checklist when applicable | C |
| **Reliability & concurrency** | Failure, repeat, restart and concurrency behavior respects business invariants | Retry/duplicate delivery, lost updates, races, idempotency, transaction/outbox/compensation assumptions, cleanup and backpressure | C |
| **Efficiency & resource lifecycle** | Relevant workload fits latency, throughput and resource constraints without wasteful hot-path behavior | N+1/scan, repeated I/O, algorithmic growth, caching bounds, resource leaks; compare representative before/after signals | C |
| **Operability & evolution** | Failures are detectable and recoverable; changes can be deployed, diagnosed and safely evolved | Useful errors/logs/metrics/traces, configuration defaults, rolling-version compatibility, migrations, rollback and incident history | C |

These are **quality dimensions, not eight mandatory checks**. Pick the few with credible exposure for this change. Existing CI/static analysis/language tooling should handle routine style and syntax; reviewers concentrate on semantic and engineering decisions.

## B: practical reuse decision

Before recommending a new common abstraction, check:

- Is there a **current** helper, module, service or policy that already expresses the *same behavior* (including failure and authorization semantics)?
- Does reuse preserve **domain ownership**, dependency direction and future change independence?
- Are repeated fixes or diverging business decisions creating **observable maintenance or correctness cost**?
- Would extraction actually **reduce** total complexity, rather than just reduce line duplication?

Decision ladder: **reuse existing correct implementation → module-local extraction when repeated → shared technical library for independently repeated stable cross-module utility → shared domain service/policy for the same business rule**. Deliberately **keep separate** different concepts that merely look similar. Do not mandate an arbitrary duplication count, SOLID slogan, file-length threshold or new library absent supporting evidence.

Compare current code first, then directly related callers, then shared libraries, then selective Git history. Historical behavior is useful context **but may itself be wrong**.

## Test quality: verify the guardrail, not just a green build

For material changes, identify the highest-risk behavior and one test or focused probe able to catch its failure:

- **Wrong positive result:** test should detect false success, unauthorized access or wrong output, not just a 200/zero exit code.
- **Failure behavior:** test a representative invalid state, missing dependency, partial failure, or repeated action *when relevant*.
- **Regression boundary:** test a caller/consumer or invariant affected by the change, not only the implementation method.
- **Test cost:** prefer focused deterministic tests; avoid duplicating the whole test suite or adding fragile fixtures solely to demonstrate review activity.

Property-based tests, targeted mutation tests, fuzzing, contract tests and failure injection are **optional escalation techniques**, selected when their risk-reduction value is credible. Never treat coverage percentages, mutation score or test count as direct proof of product quality.

## System-quality decision prompts (use only when exposed)

**Distributed / stateful:** Which operation must happen once versus at least once? Who owns retries? What if a message is duplicated, reordered or lost, or one step commits while another fails? Are timeout, idempotency, compensation and reconciliation semantics clear?

**Performance:** What is the actual expected workload and baseline? Is there a measurable expensive operation on a hot path? Avoid claiming a regression based only on theoretical complexity without relevant input sizes or a clear blow-up mechanism.

**Security:** Where does trust cross a process/user/tenant boundary? Is authorization enforced at the trusted server/service boundary, not only the UI? Prefer project-approved controls and libraries; never invent a universal security rule when the contract and threat model matter.

**Operations:** If this breaks after rollout, how will it be detected, diagnosed, contained and rolled back? Do old/new versions and existing data coexist safely? Select observability signals that correspond to real failure modes; do not demand new infrastructure for a cosmetic change.

## Findings, severity and stopping

- **Block** only a proven requirement/contract/invariant violation, a material regression introduced or worsened by the change, or a significant safety/production risk with a credible mechanism.
- **Suggest** non-critical refactors, clarity improvements or opportunities for reuse, explaining the trade-off; do not automatically broaden the change scope.
- **Record as unknown** cases without a trustworthy requirement, baseline or feasible runtime evidence. Escalate essential business decisions to the human.
- Finish after relevant coverage and targeted repair verification under the stopping rules in `SKILL.md`; **not** when every stylistic preference has been satisfied.

Use **evidence-supported qualitative judgments**, not a blanket numerical "code quality score." The 0–6 number in the main Skill is a **review allocation/risk heuristic**, not a quality grade.

## Source grounding (further reading, not mandatory to load)

These are independently maintained external references. They provide principles; **this file is a selective adaptation, not a claim of formal certification, mandated compliance, or reproduction of their full checklists**.

- [Google Engineering Practices — What to look for](https://google.github.io/eng-practices/review/reviewer/looking-for.html): design, functionality, unnecessary complexity, tests, names and documentation.
- [Google Engineering Practices — The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html): improve code health while allowing reasonable forward progress.
- [Microsoft Engineering Playbook — Reviewer Guidance](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/process-guidance/reviewer-guidance/): focus on business logic, test quality, design and maintainability beyond automatable checks.
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/definitions.html): operational excellence, security, reliability and performance among system-level attributes.
- [OWASP Application Security Verification Standard](https://owasp.org/projects/asvs): security requirements and verifiable controls for relevant application surfaces.
- [ISO/IEC 25010:2023 product quality model](https://www.iso.org/standard/78176.html): broad product-quality attributes for specification and evaluation; it does not prescribe this skill's pass/fail policy.
- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/): useful production signals (latency, traffic, errors, saturation) when runtime monitoring is in scope.
