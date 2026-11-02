# Behavioral Testing & Requirement Boundaries

**Read on material behavioral changes only.** This is an A/B/C review aid, not a new reviewer, test-count quota, mandatory full E2E suite or approval process for every bug. Review the **test cases themselves**, not just green CI or coverage percentages. Read the project's applicable testing conventions first.

## 1. Establish the correct behavioral oracle

Independently derive the observable behavior from the user's **approved request**, acceptance criteria, established domain/API contracts and justified safety invariants. Neither production code nor existing tests automatically define the right behavior.

Favor **black-box testing** at a stable public boundary (API, service contract, UI action, CLI, message handler): specify **Given** initial state/actor, **When** action or event, **Then** observable result, side effects and persisted state. Challenge tests that only check HTTP 200, call count, a mock invocation, a snapshot or an exit status.

Black-box is a perspective, **not a command to create expensive browser E2E tests**. Focused API/contract/integration tests can provide stronger, faster evidence. Mocking is reasonable at unrelated external boundaries, but must not bypass the very authorization, persistence or error behavior under review.

## 2. Choose meaningful scenarios beyond the happy path

| Family | Test the failure mechanism when exposed by the change |
| --- | --- |
| **Normal outcome** | Approved input → expected business output and side effects |
| **Negative / security** | Invalid or missing inputs, forbidden roles, cross-tenant ownership, rejected transitions |
| **Multi-step business chain** | Earlier writes/state affect later decisions, dependent steps, cancellation, resume and final state |
| **Data consistency** | Persist/rollback rules, uniqueness, ordering, duplicate side effects, transaction failures |
| **Failure & retry** | Timeout, partial failure, repeat request, stale data, restart or recovery where applicable |
| **Concurrency and scale** | Two actors racing, out-of-order delivery, load/cardinality only when plausible |
| **Compatibility** | Relevant consumers, historical data, old/new versions and public contract behavior |

**Illustrative multi-step scenario:** actor enters context → authorization → create/update → persistence → external notification → read-back. Verify the final state and any necessary invariant at each critical seam. Repeat the *highest-risk divergent route*, such as a foreign actor, timeout after persistence or duplicate submission, **only if the business semantics are already established**. This example illustrates how to test a chain; it is not a new product requirement.

Use the smallest reliable scenario set that exposes **distinct material risks**. Do not construct an exhaustive Cartesian product, duplicate every test at every layer or make routine changes wait for flaky/expensive full-system suites.

## 3. Audit tests as first-class review targets

- **Happy-path-only:** test fixtures and assertions permit only successful calls despite relevant denial, invalid state, repeated action or failure modes.
- **Implementation-mirroring:** expected values derived from the same function/branch or a mock always returning what the implementation expects.
- **Weak oracle:** checks only status/return type, not resulting business state, authorization, downstream effects, rollback or idempotency.
- **Fake integration:** all important boundaries are stubbed, but the test claims to verify multi-service behavior.
- **Flaky or brittle tests:** nondeterministic setup, shared mutable fixtures, timing guesses, excessive implementation detail and no helpful diagnostics.

Ask: **Would a realistic wrong implementation pass this test?** If yes, name a specific missing observable assertion or scenario and its practical risk. State whether the test was actually executed; never invent outputs.

## 4. Do not promote unspecified business rules into requirements

Identifying an omitted edge case does not authorize a new product policy. Classify it before suggesting implementation:

| Situation | Appropriate action |
| --- | --- |
| **Confirmed violation of an approved requirement** | Report and repair within the authorized scope; test the agreed behavior |
| **Established invariant / binding safety contract** | Verify evidence and address a proven violation; promptly escalate major security/data risks |
| **Material ambiguity blocking the requested work** | Explain evidence and exact alternatives; **obtain explicit user confirmation** before implementing one interpretation or writing acceptance tests that assert it. Use NEEDS_DECISION only if truly blocking |
| **New business rule or new behavior absent from request/contracts** | Present a **proposed requirement**, triggering scenario, user impact and options/recommendation; **wait for explicit user approval before formally adopting, implementing or encoding it into an acceptance test** |
| **Unrelated technical debt or speculative improvement** | Non-blocking suggestion; do not silently expand task scope |

Diagnostic tests can observe actual behavior without assuming a policy, but must not claim an invented expected outcome is approved. A new rule about ownership, retries, finance, privacy, tenant boundaries, state transitions or fallback behavior particularly needs a confirmed product/contract basis.

**Ask concisely:** "When [state/action] happens, the current behavior is [evidence]. The requested behavior is unspecified. Should the system [A] or [B]? I recommend [option] because [reason]." Wait for approval before implementing the **new** rule. When a candidate enhancement is independent, deliver the existing authorized work and report the suggestion separately; don't block it.

## 5. Review roles and evidence

- **A:** derive the black-box oracle, verify relevant negative/multi-step acceptance behavior, identify unapproved new product rules.
- **B:** inspect test assertions, fixture realism, project test conventions and integration boundaries, not just code structure.
- **C:** select focused reliability, authorization, concurrency, persistence and recovery scenarios where actual risk justifies them.
- **Parent:** reconcile to approved scope. If user confirmation is essential, request it rather than guessing. Do not silently extend functionality.

Output relevant test locations, observable expected/actual behavior, executed commands/results when available, missing material coverage, and precise questions for user decisions. Respect the existing one-round review, targeted re-verification and no endless PASS-loop policy.

## Industry references

- [Microsoft Engineering Playbook — Test planning](https://microsoft.github.io/code-with-engineering-playbook/automated-testing/test-planning/)
- [Google Developers — Unit, integration, behavior and functional testing](https://developers.google.com/solutions/content-driven/backend/testing)
- [Google Testing Blog — Good end-to-end tests](https://testing.googleblog.com/2016/09/testing-on-toilet-what-makes-good-end.html)
- [Microsoft Azure Well-Architected — Testing strategies](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/testing)
