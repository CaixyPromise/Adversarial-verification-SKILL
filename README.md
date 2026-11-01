# Adversarial Verification

A lightweight, **requirement-driven and risk-adaptive** code-review skill for AI coding agents.

It reviews whether an implementation meets the **actual user intent**, preserves business invariants, and avoids material regressions. Independent adversarial verification remains available, but is **not a compulsory ritual** for trivial changes. Findings and evidence matter more than obtaining a PASS label.

中文说明：[README_zh.md](./README_zh.md)

## How it works

1. **Understand:** determine intended behavior, key business flow, invariants and material unknowns from the user request and codebase.
2. **Assess:** score complexity, impact and uncertainty, 0–2 each; total 0–6.
3. **Review:** cover requirements, affected paths, regressions and relevant technical risks in one broad round.
4. **Resolve:** address proven blockers at their root cause and ask a human for material unresolved business decisions.
5. **Finish:** targeted re-verification, explicit coverage and residual risks; no indefinite PASS-chasing loop.

## Review budget: up to three verifier subagents

| Risk score | Default verifier subagents | Typical use |
| --- | --- | --- |
| 0–1 | 0 | Cosmetic or isolated, directly check the result |
| 2–3 | 1 | Focused feature/behavior check |
| 4–5 | 2 | Business flow and a distinct technical risk |
| 6 | 3 | Complementary business, safety/state and regression perspectives |

A third verifier is also allowed for a 4–5 score when a distinct material risk justifies it. **Three is a cap, not a quota**; do not assign multiple agents the same question. Serious security/authorization, data-integrity, financial or irreversible operations receive elevated scrutiny even for short diffs. If business rules are materially unclear, clarify the decision instead of guessing.

Example three-way split:
- Reviewer A: user requirements, critical business flow and invariants.
- Reviewer B: security, data integrity, state transitions or concurrency.
- Reviewer C: integration, compatibility, regressions and operations.

## Result format

- `READY`: applicable coverage sufficient, no known blockers in reviewed scope.
- `CHANGES_NEEDED`: verified blocking defects remain.
- `NEEDS_DECISION`: a material business/product decision is missing.
- `PARTIAL`: required evidence or verification environment is unavailable.

These are **delivery assessments**, not mathematical claims of correctness or production approval. Every blocking finding needs a specific violated rule, trigger, code/runtime evidence, impact, and repair direction. Improvements and open hypotheses are separate.

One broad review round is the default. Fixes receive targeted re-verification of the issue and affected paths. After two unsuccessful repair cycles for the same blocker, stop automatic looping and escalate with evidence.

## Files

- `SKILL.md` — authoritative workflow and 0–3 agent allocation.
- `references/review-playbook.md` — optional domain-specific probes, read only when relevant.
- `references/security-review-checklist.md` — optional security guidance.
- `agents/openai.yaml` — skill interface metadata.

## Install in Codex

The repository **root** is the skill directory; it contains `SKILL.md` directly.

```bash
export CODEX_HOME="$HOME/.codex" # change if you use a custom CODEX_HOME
mkdir -p "$CODEX_HOME/skills/adversarial-verification"
curl -fsSL "https://github.com/CaixyPromise/Adversarial-verification-SKILL/archive/refs/heads/main.tar.gz" \
  | tar -xz --strip-components=1 -C "$CODEX_HOME/skills/adversarial-verification"
```

Restart Codex after installation. For development, clone the repository directly into the same destination instead.

## Migration from v0.1

The old `PASS/FAIL/PARTIAL` contract and 11 category-specific prompt templates have been replaced by a requirement-first decision and a compact on-demand playbook. **Update any integrations parsing the old verdict strings.** The original independent, read-only verifier concept and root-cause repair policy remain.

## License

MIT.
