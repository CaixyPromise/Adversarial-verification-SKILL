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

A third verifier is also allowed for a 4–5 score when a distinct material risk justifies it. **Three is a cap, not a quota**; do not assign multiple agents the same question. Serious security/authorization, data-integrity, financial or irreversible operations receive elevated scrutiny even for short diffs. If business rules are materially unclear, resolve them from evidence or ask for a decision before multiplying reviewers; ambiguity alone does not justify more agents.

### Reviewer roles and how they review

- **A — Requirement correctness:** independently derive acceptance criteria and business invariants, trace the full intended journey and find semantic mistakes or missing scenarios.
- **B — Implementation consistency:** search progressively (changed module → direct dependencies → relevant shared code → selective history), compare established code and business semantics, and prefer existing reuse or module-local extraction. A shared utility package is appropriate only when stable cross-module technical behavior recurs; shared business rules belong in domain services/policies. **Never abstract merely because code looks similar.**
- **C — System engineering:** assess applicable performance, security, long-term maintenance, system compatibility and distributed failure/concurrency risks using targeted probes.

With **one** reviewer, cover all three lenses in proportion to risk. With **two**, default to A and combined B+C (or split differently for the dominant risk); parent checks gaps. With **three**, assign A/B/C separately. Role-specific investigation guidance is in `references/review-playbook.md`. No role is a reason to demand refactoring purely for reuse.

## Result format

- `READY`: applicable coverage sufficient, no known blockers in reviewed scope.
- `CHANGES_NEEDED`: verified blocking defects remain.
- `NEEDS_DECISION`: a material business/product decision is missing.
- `PARTIAL`: required evidence or verification environment is unavailable.

These are **delivery assessments**, not mathematical claims of correctness or production approval. Reviewers **independently derive expected behavior** from the request and trusted contracts before accepting the implementer's rationale. Where feasible, compare baseline and changed behavior and label findings **introduced / worsened / pre-existing / unknown**. Keep unrelated existing problems out of the current repair scope while escalating serious historical safety issues. Every blocking finding needs a specific violated rule, trigger, code/runtime evidence, impact, and repair direction. Improvements and open hypotheses are separate.

One broad review round is the default. Fixes receive targeted re-verification of the issue and affected paths. After two unsuccessful repair cycles for the same blocker, stop automatic looping and escalate with evidence.

## Files

- `SKILL.md` — authoritative workflow and 0–3 agent allocation.
- `references/review-playbook.md` — role-specific investigation methods and optional engineering probes.
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
