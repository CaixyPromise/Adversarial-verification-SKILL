# Parent Agent Workflow

This file provides a complete workflow template for a parent agent that implements code and then launches a verifier subagent.

## Core contract

The parent agent owns delivery, but does not own the final verdict for non-trivial implementation work.

The verifier subagent owns the verification verdict.

The parent agent must not self-certify non-trivial work by saying:

- “looks good”
- “tests pass so we are done”
- “probably fine”
- “PARTIAL because I have caveats”

If the work is non-trivial, the parent agent should launch the verifier.

## What counts as non-trivial

Treat the work as non-trivial when any of these apply:

- 3 or more file edits
- backend/API changes
- frontend behavior changes
- database or migration changes
- infrastructure or config changes
- concurrency, caching, auth, or state management changes
- any change where the happy path passing is not enough confidence

## Parent agent workflow

1. Implement the requested change.
2. Summarize for yourself what changed:
   - original request
   - changed files
   - implementation approach
   - known risk areas
3. Decide whether the work is non-trivial.
4. If trivial, you may report completion without verifier escalation, but only when that judgment is actually defensible.
5. If non-trivial, launch a fresh verifier subagent.
6. Wait for the verifier result.
7. If verifier returns `FAIL`, fix the issue and re-run verifier.
8. If verifier returns `PASS`, optionally spot-check 1-2 commands from the verifier report.
9. If verifier returns `PARTIAL`, report exactly what was verified and what could not be verified.

## What the parent agent should pass to the verifier

Pass the minimum necessary task-local context:

- original user request
- changed files
- implementation summary
- success criteria or plan path if available
- suggested run/build/test commands if non-obvious

Do not pass:

- your own conclusion that the code is correct
- your own PASS/FAIL judgment
- hidden expected answers unless contract checking truly requires them
- a request to “confirm this is fine”

## Parent prompt template

Use this when launching the verifier subagent:

```text
Use the adversarial-verification skill at /Users/caixypromise/.codex/skills/adversarial-verification to independently verify this implementation.

Original user request:
[paste]

Changed files:
[paste]

Implementation summary:
[paste]

Success criteria / plan path:
[optional]

Suggested commands:
[optional]

Requirements:
- Treat this as non-trivial implementation verification.
- Do not modify project files.
- Run the feature directly, not just tests.
- Run at least one adversarial probe.
- If this is frontend-heavy, use the frontend-specific verifier prompt.
- If this is backend/API-heavy, use the backend/API-specific verifier prompt.
- If this is migration/database-heavy, use the migration/database-specific verifier prompt.
- If this is CLI/script-heavy, use the CLI/script-specific verifier prompt.
- If this is security-sensitive, use the security/penetration-specific verifier prompt.
- If this is performance/scalability-sensitive, use the performance/scalability-specific verifier prompt.
- If this is data-pipeline/async-job-heavy, use the data-pipeline/async-job-specific verifier prompt.
- If this is mobile/desktop-client-heavy, use the mobile/desktop-client-specific verifier prompt.
- If this is infra/deployment/ops-heavy, use the infra/deployment/ops-specific verifier prompt.
- If this is LLM/agent-workflow-heavy, use the LLM/agent-workflow-specific verifier prompt.
- If the implementation appears to pass tests by distorting the business behavior or gaming fixtures, call that out explicitly.
- End with exactly one of: VERDICT: PASS / VERDICT: FAIL / VERDICT: PARTIAL.
```

## Parent-side anti-patterns

The parent agent should not:

- ask the verifier to rubber-stamp the implementation
- preload the verifier with “tests already pass, just confirm”
- hide risky files or known failure areas
- ask the verifier to fix code instead of verify it
- reinterpret verifier FAIL as acceptable if the failure is actionable

## How the parent should react to verifier outcomes

### If verifier says PASS

Parent should:

- optionally re-run 1-2 high-signal commands from the verifier report
- report completion cleanly
- preserve the verifier's conclusion without watering it down

### If verifier says FAIL

Parent should:

- treat FAIL as a delivery blocker
- read `references/main-thread-discipline.md` before making repair edits
- fix the root cause, not only the symptom
- re-run the verifier with updated context

### If verifier says PARTIAL

Parent should:

- report the verified scope
- report the unverified scope
- explain the environmental limitation
- not reframe PARTIAL as PASS

## Root-cause discipline

The parent agent must explicitly avoid “water more flour, flour more water” fixes such as:

- special-casing the fixture
- hardcoding values only for current tests
- swallowing exceptions to keep outputs green
- widening contracts so that bad inputs stop failing visibly
- adding retries/timeouts/guards that mask the real defect without resolving it

If the verifier identifies one of these patterns, the parent agent should fix the root cause instead of negotiating with the verdict.

## Additional parent-side policies

- Read `references/root-cause-fix-policy.md` when the verifier returns `FAIL` and the parent agent needs a disciplined repair flow.
- Read `references/main-thread-discipline.md` before any post-FAIL repair work. This is mandatory, not optional, when the parent agent is at risk of overfitting to fixtures, weakening contracts, or changing behavior without understanding the business reason.
- Read `references/security-review-checklist.md` when the verifier needs a structured security review output for security-sensitive work.
