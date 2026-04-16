---
name: adversarial-verification
description: Independent adversarial verification for non-trivial implementation work. Use when Codex should launch a separate subagent to validate code changes before reporting completion, especially after 3+ file edits, backend/API changes, infrastructure changes, migrations, risky frontend work, or any implementation where self-review is not enough. Triggers on requests to independently verify, adversarially test, second-opinion review, try to break the implementation, or gate completion with PASS/FAIL/PARTIAL evidence.
---

# Adversarial Verification

Launch a separate verifier subagent for non-trivial implementation work. The verifier's job is not to confirm the code looks correct. Its job is to try to break the change, gather execution evidence, and issue a verdict.

## Quick start

When subagents are available, use a fresh subagent for verification after implementation is complete.

Pass the verifier only the minimum task-local context it needs:

- original user request
- changed files
- implementation summary
- success criteria or plan path if one exists
- relevant run/build/test commands if they are non-obvious

Do not pass your own conclusion. Do not tell the verifier that the code is probably correct. Do not preload expected outcomes unless the task requires exact contract checking.

## Hard rules for the verifier

The verifier must:

- not modify project files
- not install dependencies
- not perform git write operations
- treat passing tests as context, not proof
- run the feature directly instead of only reading code
- include exact commands and observed outputs in its report
- check business correctness, not only mechanical correctness
- call out fixes that merely game tests instead of solving the underlying problem
- end with exactly one of: `VERDICT: PASS`, `VERDICT: FAIL`, `VERDICT: PARTIAL`

Temporary scripts are allowed only under `/tmp` or `$TMPDIR` when needed for multi-step probes.

## Parent agent workflow

1. Finish the implementation.
2. Decide whether the work is non-trivial.
3. If non-trivial, launch a fresh verifier subagent.
4. Wait for the verifier's report.
5. If `FAIL`, fix the issue and re-run the verifier.
6. If `PASS`, optionally spot-check 1-2 commands from the verifier report before reporting completion.
7. If `PARTIAL`, report exactly what was verified and what could not be verified.

## What counts as non-trivial

Treat the work as non-trivial when any of these apply:

- 3 or more file edits
- backend or API behavior changed
- infrastructure or config behavior changed
- database or migration work changed
- frontend behavior changed in a way that needs runtime interaction
- the change can regress neighboring behavior even if the happy path passes

## Verifier checklist

The verifier should perform, at minimum:

1. Build / test / lint / type-check if applicable.
2. Run the changed functionality directly.
3. Run at least one adversarial probe.
4. Check observed output, not just exit status or HTTP status.
5. Issue a PASS / FAIL / PARTIAL verdict with evidence.
6. Expand into non-functional review domains when relevant: performance, database/query design, memory/resource lifecycle, security, and business correctness.

For adversarial probes and change-type-specific tactics, read `references/playbook.md`. For broader review domains and anti-cheating rules, read `references/domain-checklists.md`. For security-sensitive work where the verifier needs a structured reporting frame, read `references/security-review-checklist.md`. For parent-agent response to verifier FAIL and disciplined repair behavior, read `references/root-cause-fix-policy.md` and `references/main-thread-discipline.md`.

## Mandatory parent-agent reading

The parent/main thread must read and understand `references/main-thread-discipline.md` before making post-verification repairs or debug-driven behavior changes.

Treat this as mandatory, not optional guidance, when any of these apply:

- the verifier returned `FAIL`
- the parent is about to change behavior after a failing test or failing adversarial probe
- the cause is not yet clearly understood
- the possible fix changes externally visible behavior, validation, or policy

If the parent has not read `references/main-thread-discipline.md`, it should stop and read it before continuing.

## Recommended verifier prompt template

Use this as the subagent prompt:

```text
You are an independent adversarial verifier.

Your job is not to confirm the implementation probably works. Your job is to try to break it, find missing edge cases, and produce an evidence-based verdict.

You must not modify project files, install dependencies, or run git write operations. Temporary scripts are allowed only in /tmp or $TMPDIR.

Inputs:
- Original user request: [paste]
- Changed files: [paste]
- Implementation summary: [paste]
- Success criteria / plan path: [optional]
- Suggested commands: [optional]

Workflow:
1. Read project instructions and run commands.
2. Run build/test/lint/typecheck if applicable.
3. Execute the changed behavior directly.
4. Run at least one adversarial probe.
5. Report only what you actually ran.

Every check must include:
- Check
- Command run
- Output observed
- Expected vs Actual
- Result: PASS or FAIL

End with exactly one of:
VERDICT: PASS
VERDICT: FAIL
VERDICT: PARTIAL
```

## Specialized verifier templates

Keep the general verifier prompt as the default. When the change is predominantly UI/browser-facing, use the frontend-specific template. When the change is predominantly server or API behavior, use the backend/API-specific template. When the change is primarily persistence-layer work, use the migration/database-specific template. When the change is primarily a terminal tool or script surface, use the CLI/script-specific template. When the change is security-sensitive, use the security/penetration-specific template. When the change is performance- or scale-sensitive, use the performance/scalability-specific template. When the change is primarily queue, worker, scheduler, webhook-processing, or asynchronous pipeline behavior, use the data-pipeline/async-job-specific template. When the change is primarily a mobile or desktop client surface, use the mobile/desktop-client-specific template. When the change is primarily infrastructure, deployment, runtime operations, CI/CD, containerization, rollout, or incident-prone operational behavior, use the infra/deployment/ops-specific template. When the change is primarily prompt orchestration, tool use, memory/context handling, agent coordination, evaluation loops, or other LLM-agent runtime behavior, use the LLM/agent-workflow-specific template.

Selection rule:

- frontend-heavy changes: use the frontend-specific template
- backend/API-heavy changes: use the backend/API-specific template
- migration/database-heavy changes: use the migration/database-specific template
- CLI/script-heavy changes: use the CLI/script-specific template
- security-sensitive changes: use the security/penetration-specific template
- performance/scalability-sensitive changes: use the performance/scalability-specific template
- data-pipeline/async-job-heavy changes: use the data-pipeline/async-job-specific template
- mobile/desktop-client-heavy changes: use the mobile/desktop-client-specific template
- infra/deployment/ops-heavy changes: use the infra/deployment/ops-specific template
- LLM/agent-workflow-heavy changes: use the LLM/agent-workflow-specific template
- mixed full-stack changes: start from the general template and add only the relevant specialized checks

## Parent agent workflow template

Use `references/parent-workflow.md` when you want the parent agent and verifier subagent to work as a full two-stage quality gate rather than a loose review step.

## Using this skill without subagents

If subagents are unavailable, you may follow the same workflow yourself, but explicitly state that this is not a truly independent verification pass.

## References

- Read `references/playbook.md` for adversarial probe patterns.
- Read `references/domain-checklists.md` for performance, database, code quality, memory, security, and business-correctness review domains.
- Read `references/prompt-templates.md` for the general verifier prompt, frontend-specific verifier prompt, backend/API-specific verifier prompt, migration/database-specific verifier prompt, CLI/script-specific verifier prompt, security/penetration-specific verifier prompt, performance/scalability-specific verifier prompt, data-pipeline/async-job-specific verifier prompt, mobile/desktop-client-specific verifier prompt, infra/deployment/ops-specific verifier prompt, and LLM/agent-workflow-specific verifier prompt.
- Read `references/parent-workflow.md` for the full parent-agent -> verifier-subagent workflow template.
- Read `references/security-review-checklist.md` for a structured security review output format the verifier can apply directly.
- Read `references/root-cause-fix-policy.md` for how the parent agent should respond to verifier FAIL.
- Read `references/main-thread-discipline.md` for the main-thread policy against fixture-gaming, shallow patching, and user-approval bypass. This is mandatory reading for the parent/main thread before post-FAIL repair work.
