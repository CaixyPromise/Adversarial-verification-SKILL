# Reasoning Convergence & Coverage-First Delivery

**Purpose:** make review simultaneously **thorough on the relevant first pass** and **finite after repairs**. Apply these rules to the existing A/B/C roles and parent; add no reviewer, rigid test quota, mandatory report, or extra full-review round.

The two failure modes are related but distinct:
- **Unproductive qualification:** endlessly saying what cannot be inferred without stating what current evidence *does* support.
- **Drip-feed review:** finding a small subset of issues, repairing immediately, then discovering additional issues on the same unchanged paths during successive purported "re-verifications."

**Operating principle: finish a relevant, evidence-based coverage pass before routine repair; consolidate root causes; repair in coherent batches; reverify changed behavior; then deliver a bounded conclusion.**

## 1. State supported conclusions positively

Lead with the **best supported conclusion or current bounded assessment**, then its decisive evidence, only material uncertainty and the actual next action.

| Weak / prohibited pattern in this context | Useful engineering output |
| --- | --- |
| "不能证明是 Playwright，也不代表不是浏览器问题，并非一定是代码。" Repeated without evidence or action. | "浏览器在启动阶段退出；当前日志未定位责任组件。项目代码暂不修改。下一步只检查已安装的浏览器版本与启动日志；无法验证则记录环境限制。" |
| "不是所有的索引都会有效，并不意味着 N+1 一定产生瓶颈，不能确定是否优化。" With no workload analysis. | "订单列表每行触发一次关联查询，200 条记录产生 201 次 SQL 往返（实测）。建议在现有数据访问层批量查询，并验证顺序与权限。" |
| "虽然已经修复这个问题，但不能保证不存在其他问题，还需要继续全面审查。" After an adequately scoped review. | "本轮已覆盖授权、数据写入和异常分支；已修复 3 项并通过对应回归。未验证的外部服务超时场景单独列为限制；本轮停止。" |
| "不能说已完成，也不能说未完成，还要再看看。" | "当前代码修改完成，核心回归通过；浏览器 E2E 因缺少已授权的运行环境未执行。状态为 PARTIAL，交付明确列出未覆盖项。" |

This is **not a word ban** on "not", "cannot prove", "may" or "does not imply". They remain essential for material logical distinctions. Reject **repeated negation without information gain**, not responsible uncertainty. Do not turn caution into an invented affirmative conclusion.

### Material uncertainty gate

For each meaningful uncertainty, ask: **What specific evidence is missing? Would that evidence change the current verdict, repair direction, user safety or authorization? Is there a cost-appropriate way to obtain it?** If it would not change the decision, stop expanding it. If it matters but cannot be obtained, state the precise unverified scope and choose the existing READY / CHANGES_NEEDED / NEEDS_DECISION / PARTIAL assessment accurately.

## 2. Coverage-first gate: prevent serial "find one, fix one" review

A review is not complete when the first plausible defect is found. Before routinely starting repairs:

1. **Bound the review surface from the requirement and diff.** Identify affected entry points, important branches/state transitions, direct callers/consumers, domain contracts, surrounding integration, high-risk failure mechanisms and relevant tests. Do not search the entire repository without evidence of impact.
2. **Assign complementary A/B/C lenses** under the existing 0–3 agent cap. Each assigned verifier covers **its entire relevant scope**, not just the first one or two findings. With one verifier, cover applicable lenses proportionately; with none, the parent performs the bounded review.
3. **Collect findings without interrupting the coverage pass.** Record confirmed defects and their evidence; continue examining the remaining *material* paths and scenario families. Only stop early for a genuine blocker to further inspection, urgent safety concern or necessary user decision—then explicitly state the scope not yet covered.
4. **Synthesize before ordinary repair.** The parent checks every assigned relevant scope for a coverage result, merges duplicate/root-related issues, tests weak hypotheses and produces **one consolidated list**: confirmed blockers, non-blocking improvements, candidate user decisions and unverified material gaps.
5. **Batch repairs by root cause and dependency.** Repair the confirmed issues in a coherent implementation pass (with small controlled commits when useful), then test the repaired behavior and its coupled regression paths. Independent severe safety fixes may be prioritized immediately, but must not silently abandon the remainder of the initial review.

### What counts as meaningful coverage?

A verifier's handoff states **which code paths and business branches were inspected; which relevant tests/assertions were examined or executed; what material areas remain unreviewed and why**. Coverage is assessed against **the scoped risk surface**, not against every line, category or theoretical scenario. A statement such as "checked the code, found one bug" with no scoped coverage evidence is **not a finished review**.

Use the cheapest decisive evidence; do not invent coverage percentages or require all E2E tests. For large changes, the scope can be partitioned so reviewers finish their parts before synthesis.

## 3. Batched repair and bounded re-verification

After one consolidated review:

- **Prioritize shared root causes and impacted dependencies**; avoid separate repairs for several manifestations of the same defect.
- **Do not change business policy** or add speculative refactors while fixing the batch. Unapproved requirements go to D### user decisions rather than getting "fixed."
- **Targeted re-verification** must check each repaired failure mechanism, associated contract/invariant, and any *new* paths changed by the repair.
- A re-verification is **not another delayed broad discovery sweep** through unchanged parts of the original scope.

If a new finding surfaces after repair, classify it **before** starting another iteration:

| New finding source | Next action |
| --- | --- |
| **Introduced by repair** | Fix the repair regression; targeted reverify. |
| **Present in original review scope but missed** | Admit a **coverage gap**, inspect the affected scope and related paths *together*; consolidate remaining findings before another coherent repair. Do not silently call this normal re-verification. |
| **Newly exposed by a material expansion** | Re-scope **only the affected new surface**. No unconditional restart of all reviewers. |
| **Pre-existing and unrelated** | Report separately, unless a confirmed critical safety or integrity issue warrants escalation. |
| **Upstream/environment/unknown** | Follow the failure-attribution reference; do not force a project patch or new browser installation. |

The existing rule to stop after two unsuccessful repair-and-reverify cycles for **the same blocker** remains. That limit prevents repeated guesses; it **does not excuse an incomplete first review**. Never label incomplete coverage READY simply to end the cycle. Where essential verification is blocked, state PARTIAL/NEEDS_DECISION as appropriate; confirmed blockers remain CHANGES_NEEDED.

## 4. Progress and stopping rule

An investigation attempt should yield at least one of: **new evidence; eliminated or narrowed hypothesis; clarified ownership/affected surface; concrete repair or delivery decision**. Rewording the same uncertainty is not progress.

After **two consecutive attempts on the same question with no material progress**, stop that line of investigation and either:
- use existing evidence to make a bounded decision;
- make one **distinct, high-value and low-cost** verification attempt if it could change the decision;
- or report a precise blocker, missing evidence or required authorization.

This refers to **observable investigation attempts**, not hidden reasoning tokens. It never permits skipping required security, authorization, financial or data-integrity validation.

**Decision sufficiency:** once the relevant risk surface has been covered, fixes verified and additional investigation is unlikely to affect the current authorized decision, stop. Theoretical alternative explanations alone are not a reason to continue.

## 5. Reference examples — apply to actual Review output

### Counterexample: serial superficial review

- First pass: find missing authorization, stop; parent repairs it.
- "Re-review": notice N+1 query in the **unchanged code**; stop; parent repairs it.
- "Re-review": notice failed rollback in the **same original transaction path**; start another full cycle.

**Correct execution:** derive the business path once; A checks allowed/denied state transitions, B checks direct callers, reuse and test quality, C checks authorization, query shape and transaction failure. Consolidate **F001 authorization**, **F002 N+1** and **F003 rollback** with concrete evidence, then repair shared causes in a coherent batch and run focused negative/transaction/throughput regression tests. If a blocker truly prevents further examination, record the explicit coverage gap instead of pretending the first pass was complete.

### Reference final delivery

**结论：** 本轮已覆盖订单克隆的鉴权、数据写入、事务回滚及受影响调用链。确认 3 项缺陷，集中修复并完成定向回归；评估为 READY。

**依据：** 权限拒绝测试、批量查询次数对比和故障回滚断言均通过；结果与原需求及既有契约一致。

**边界：** 未执行不在本次部署范围内的第三方服务故障注入，不影响当前验收结论。

**行动：** 已完成修复及验证，可进入下一交付环节。

This example is illustrative, **not evidence that any real project was tested or repaired**. Report only commands actually run, findings actually proved and genuine unresolved risks. Keep output concise; do not expand every minor caveat into a new subsection.

## Reviewer and parent responsibilities

- **A:** finish applicable requirement branches, business states and behavioral test review before returning findings.
- **B:** complete scoped implementation, direct dependencies, contract and pragmatic reuse consistency instead of finding one style issue and exiting.
- **C:** finish applicable security, persistence, concurrency, performance and failure-ownership risks instead of stopping at the first failing test.
- **Parent:** act as the **coverage-completeness and batch-repair gate**: request remaining scoped evidence from incomplete reviewers *before routine repair*, synthesize findings once, repair coherently, then run targeted verification and deliver one meaningful verdict.

**Do not substitute a large generic checklist, arbitrary minimum number of findings, or agent count escalation for evidence-based scoped completeness.**
