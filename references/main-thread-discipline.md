# Main-Thread Discipline

Use this to constrain the parent/main thread after verification findings or during debugging.

The main thread is responsible for understanding the feature or business behavior being implemented. It must not drift into fixture-gaming or random patching just to get back to green.

## Mandatory policy

This file is mandatory reading for the parent/main thread before:

- reacting to verifier `FAIL`
- changing logic after a failing test or adversarial probe
- changing validation, retries, fallbacks, or externally visible behavior under uncertainty

If the parent has not read and understood this policy, it should stop and do that before editing.

## Core principle

Do not solve “how do I make this test pass”. Solve “why is the system behaving incorrectly for the actual feature or business requirement”.

## Required main-thread behavior

- reason from the user request, product intent, and runtime behavior
- reproduce the issue directly whenever possible
- inspect logs, state transitions, and outputs before changing logic blindly
- add temporary logs or diagnostics when the cause is unclear
- pause and ask the user when the correct behavior is ambiguous
- keep fixes aligned with the real workflow, not just the current sample

## Stop-signs

If any of these appear, stop and reassess instead of editing more code:

- “I can probably just special-case this input.”
- “I can relax the validation and the test will pass.”
- “I do not actually know why this is failing, but this patch might hide it.”
- “I am changing behavior that the user did not clearly ask to change.”
- “I am about to edit tests or fixtures before I understand the defect.”

## Anti-patterns

The main thread must avoid:

- water-more-flour, flour-more-water patching
- hardcoding against the current example
- changing behavior purely to satisfy one assertion
- making the system more permissive so failures disappear
- piling on retries/timeouts/null-guards without understanding causality
- editing tests to fit the implementation unless the user confirmed the spec was wrong

## Preferred debugging loop

1. Restate the intended business/feature behavior.
2. Reproduce the failure.
3. Inspect logs, outputs, and relevant state.
4. Add temporary diagnostics if needed.
5. Identify the real cause.
6. Make the minimal behaviorally correct fix.
7. Re-run the failing scenario.
8. Re-run verification.

## User-confirmation rule

Ask the user before making a change when:
- the behavior is underspecified or ambiguous
- the fix changes externally visible semantics
- multiple plausible policies exist
- the “fix” really amounts to a product decision

Do not make that decision unilaterally.

When in doubt, stop and ask. Do not spend that ambiguity budget by silently picking one interpretation yourself.

## Quality bar

A good main-thread fix should still look correct if:
- the current test fixture changes
- a different adversarial sample is used
- the verifier adds one more hostile probe
- the user evaluates the behavior in business terms instead of test terms
