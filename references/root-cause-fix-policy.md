# Root-Cause Fix Policy

Use this when the verifier returns `FAIL` and the parent agent needs to decide how to respond.

The parent agent must treat `FAIL` as a delivery blocker, not as negotiation material.

## Core rule

Fix the root cause that breaks the business or functional behavior. Do not merely make the current test, fixture, or demo path go green.

## Required response to verifier FAIL

1. Read the verifier report carefully.
2. Identify the concrete failing behavior in business terms, not only test terms.
3. Reproduce the failure directly.
4. Trace the failure through the real runtime path.
5. Add temporary diagnostics or logging when the cause is unclear.
6. Form a root-cause hypothesis.
7. Change the implementation to address that root cause.
8. Re-run the failing scenario first.
9. Re-run the verifier.

## What counts as root-cause work

Good root-cause work usually looks like:
- fixing the wrong state transition
- restoring a missing authorization or ownership check
- correcting query shape, lifecycle behavior, or retry semantics
- fixing the actual edge-case handling instead of muting the symptom
- improving observability just enough to identify the true defect before changing behavior

## Forbidden responses to FAIL

Do not respond to verifier FAIL by doing any of these unless the user explicitly approves a spec change:

- hardcoding values just for the current fixture
- special-casing the exact failing sample input
- swallowing exceptions or forcing success responses
- weakening validation so the bad input stops failing visibly
- adding retries, sleeps, or guards that hide the real defect without resolving it
- changing tests to match the bug instead of fixing the implementation
- removing assertions or checks that were correctly catching the issue

## Logging and diagnostics policy

If the cause is unclear, add temporary diagnostics and reproduce.

Prefer:
- targeted logs around state transitions
- structured logs for key identifiers, branches, and dependency responses
- one-off repro commands or temporary scripts under `/tmp`
- checking existing logs/metrics/traces before guessing

Do not keep changing logic while the actual cause is still unclear.

## When test changes are allowed

Changing tests is allowed only under a strict rule set.

You may change a test only when all of these are true:

1. you can explain in business or contract terms why the existing test is wrong or outdated
2. the implementation behavior is already correct, or the implementation fix and test fix are being made together for the same real contract
3. the test change preserves or improves coverage of the intended behavior rather than weakening it
4. you are not changing the test merely because it exposed an inconvenient but real defect

Additional rule:

- If the test change implies a product decision, external contract change, or visible semantic change, ask the user first.

Do not change tests when any of these are true:

- the test is the first thing that revealed the defect and you have not fixed the underlying behavior
- you cannot yet explain the real system-level cause of the failure
- the change would simply remove an assertion, loosen expected output, or narrow the sample so the bug stops showing up
- you are using the test edit to avoid reproducing, diagnosing, or understanding the failure

## User-confirmation rule

If the verifier failure reveals a product ambiguity, contract ambiguity, or business-rule ambiguity, stop and ask the user.

Examples:
- two plausible behaviors could both be justified
- fixing the failure would change externally visible behavior or API contract
- the only apparent “fix” is really a product decision, not an engineering correction

In those cases, do not silently choose one interpretation.

## Decision test before committing a fix

Before accepting a repair, ask:
- Does this fix the real business/functional failure?
- Would this still be the right change if the current fixture disappeared?
- Can I explain the defect and fix in system terms, not just test terms?
- Did I reproduce and observe the failure directly?

If the answer to any of these is no, the work is not ready.
