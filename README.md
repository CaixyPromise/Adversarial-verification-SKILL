# adversarial-verification

An adversarial verification skill for agentic coding workflows.

This SKILL is inspired by Claude Code's adversarial verification and verifier-agent design, then repackaged as a standalone skill that can be reused by other coding agents.

Chinese version: [`README_zh.md`](./README_zh.md)

This skill is designed to force a clean separation between:

- the implementation agent
- the independent verifier subagent
- the parent/main thread that must respond to verifier failures with root-cause discipline

The core idea is simple:

- the verifier is not there to confirm that things “probably work”
- the verifier is there to try to break the change
- the main thread is not allowed to game fixtures or patch blindly just to get back to green

## What this skill is for

Use this skill when you want an AI coding workflow to enforce a stronger software-quality gate after non-trivial implementation work.

It is especially useful for:

- backend and API changes
- frontend flows with runtime interaction risk
- database and migration changes
- shell, CLI, and automation surfaces
- security-sensitive paths
- performance-sensitive or scale-sensitive work
- data pipelines and async jobs
- mobile or desktop client behavior
- infra, deployment, and ops changes
- LLM and multi-agent workflow changes

## What is included

- `SKILL.md`: the main skill entrypoint
- `agents/openai.yaml`: agent wiring/config scaffold
- `references/playbook.md`: adversarial probe patterns
- `references/domain-checklists.md`: performance, database, memory, security, business-correctness, and anti-cheating review domains
- `references/prompt-templates.md`: reusable verifier prompts by change type
- `references/parent-workflow.md`: parent-agent to verifier-subagent workflow
- `references/security-review-checklist.md`: structured security review checklist
- `references/root-cause-fix-policy.md`: rules for how the main thread should respond to verifier `FAIL`
- `references/main-thread-discipline.md`: hard constraints against fixture-gaming, shallow patching, and user-approval bypass

## Install in Codex

This skill is packaged so it can be installed into Codex as a standalone local skill under `~/.codex/skills`.

After installation, restart Codex to pick up the new skill.

### Option 1: direct `curl` install from GitHub

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"

curl -L "https://github.com/CaixyPromise/Adversarial-verification-SKILL/archive/refs/heads/main.tar.gz" \
  | tar -xz --strip-components=2 -C "$CODEX_HOME/skills" \
      "Adversarial-verification-SKILL-main/skills/adversarial-verification"
```

### Option 2: install with Codex `skill-installer`

If already has Codex's `skill-installer` helper, the equivalent install flow is:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo CaixyPromise/Adversarial-verification-SKILL \
  --path skills/adversarial-verification
```

The direct `curl` path above is useful when you want a lightweight installation path that does not depend on the helper script.

## Design principles

This skill encodes a few strong opinions:

- verification should be independent from implementation
- passing tests is context, not proof
- happy-path validation is not enough
- the verifier should actively try to break the system
- the main thread should fix root causes, not symptoms
- ambiguous behavior changes should be escalated to the user instead of guessed

## Verifier verdict contract

The verifier is expected to end with exactly one of:

- `VERDICT: PASS`
- `VERDICT: FAIL`
- `VERDICT: PARTIAL`

The verifier should provide evidence, not vibes:

- commands run
- observed outputs
- expected vs actual behavior
- a concrete result for each check

## Specialized verifier prompts

The prompt templates currently cover:

- general
- frontend
- backend/API
- migration/database
- CLI/script
- security/penetration
- performance/scalability
- data-pipeline/async-job
- mobile/desktop-client
- infra/deployment/ops
- LLM/agent-workflow

## Usage example

### 1. Parent agent launches a verifier subagent

Use the skill after implementation is complete and the work is non-trivial.

Example parent-to-verifier prompt:

```text
Use the adversarial-verification skill in this directory to independently verify this implementation.

Original user request:
[paste request]

Changed files:
[paste changed files]

Implementation summary:
[paste summary]

Success criteria / plan path:
[optional]

Suggested commands:
[optional]

Requirements:
- Treat this as non-trivial implementation verification.
- Do not modify project files.
- Run the feature directly, not just tests.
- Run at least one adversarial probe.
- Choose the specialized verifier prompt that best matches the change type.
- If the implementation appears to pass by distorting business behavior, gaming fixtures, or weakening the contract, call that out explicitly.
- End with exactly one of: VERDICT: PASS / VERDICT: FAIL / VERDICT: PARTIAL.
```

### 2. Verifier workflow

The verifier should:

1. read project instructions and relevant run commands
2. run build/test/lint/typecheck when applicable
3. run the changed behavior directly
4. perform at least one adversarial probe
5. inspect actual output, side effects, and runtime behavior
6. issue a verdict with evidence

### 3. Main-thread behavior after `FAIL`

The parent/main thread should:

1. treat `FAIL` as a delivery blocker
2. read `references/main-thread-discipline.md`
3. read `references/root-cause-fix-policy.md`
4. reproduce the failure directly
5. add temporary diagnostics/logging when the cause is unclear
6. fix the root cause in business/functional terms
7. ask the user before making ambiguous behavior changes
8. re-run verification

## Security review usage

For security-sensitive work:

- use the security/penetration-specific verifier prompt
- use `references/security-review-checklist.md`
- lead with the highest-risk confirmed issue
- do not report `PASS` if a `Critical` or `High` issue is confirmed

## License

MIT. See `LICENSE`.
