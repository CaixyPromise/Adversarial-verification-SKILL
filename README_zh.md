# Adversarial Verification

面向 AI Coding Agent 的**需求驱动、风险自适应**代码审查 Skill。

核心目标不是不断得到 PASS，也不是尽可能找出更多问题，而是**基于真实需求和业务不变量，找出对交付有实际影响且有证据的缺陷**。简单改动不强制启动独立 Agent；复杂改动根据风险最多分配 3 个独立 Verifier。

English: [README.md](./README.md)

## 五步工作流

1. **理解需求**：明确用户想得到的行为、业务主链路、关键不变量和不确定项。
2. **风险评估**：复杂度、业务影响、需求不确定性各打 0–2 分，总分 0–6。
3. **覆盖审查**：一轮覆盖相关的需求、主链路、上下游回归和技术风险，不找到一两个问题就提前结束。
4. **根因修复**：仅将有证据的实质缺陷视为阻塞；关键业务规则无法确定时请人类决策。
5. **定向复核并结束**：验证修复点与关联回归，不为追求 PASS 无限重复完整 Review。

## 动态分配 0–3 个审查 Agent

| 评分 | 默认独立 Agent 数 | 方式 |
| --- | --- | --- |
| 0–1 | 0 | 改标题、文案等：直接检查结果 |
| 2–3 | 1 | 单功能及相关回归检查 |
| 4–5 | 2 | 业务链路与一个独立技术风险 |
| 6 | 3 | 业务、关键技术边界、集成回归分别审查 |

**最多 3 个，不是必须用满 3 个。** 在 4–5 分时，如存在第三类独立且重要的风险，也可以派发第 3 个 Agent。对于鉴权、资金、隐私、数据完整性和不可逆操作，即使改动只有几行，也必须提高审查强度。无法明确的关键业务规则，不允许 AI 擅自猜测并据此改代码。

3 个 Agent 的典型分工：
- A：用户需求、业务流程和关键不变量。
- B：权限、安全、数据完整性、并发或状态。
- C：上下游集成、兼容性、回归和运行风险。

分工随需求变化；**禁止多个 Agent 无区别地重复审查同一份 Diff**。无子 Agent 可用时，允许主 Agent 自行按同样原则检查，但需说明不具备独立性。

## 结果与停止条件

- `READY`：必要的检查覆盖充分，已审查范围内没有已知阻塞问题。
- `CHANGES_NEEDED`：仍有证据充分的阻塞性缺陷。
- `NEEDS_DECISION`：核心业务判断需要人类决定。
- `PARTIAL`：部分必要验证无法完成，说明原因和残余风险。

每条阻塞问题要有：违反的需求或约束、触发条件、代码或运行证据、实际影响和修复方向。改善建议、设计偏好和待验证假设不能直接当作阻塞缺陷。

默认只做**一轮覆盖式 Review**，修复后**定向复核**。同一个阻塞问题两次修复复核仍失败时，停止自动循环并报告原因，不能为了输出 READY 继续盲改。READY 也不意味着代码绝对无 Bug 或得到生产发布授权。

## 文件结构

- `SKILL.md`：唯一核心执行规则与 Agent 分配策略。
- `references/review-playbook.md`：按需读取的审查和对抗探测方法。
- `references/security-review-checklist.md`：安全敏感需求可选参考。
- `agents/openai.yaml`：Agent 展示与默认指令。

## Codex 安装

仓库的**根目录**就是 Skill 目录，`SKILL.md` 直接位于根目录。

```bash
export CODEX_HOME="$HOME/.codex" # 如已有自定义路径请相应修改
mkdir -p "$CODEX_HOME/skills/adversarial-verification"
curl -fsSL "https://github.com/CaixyPromise/Adversarial-verification-SKILL/archive/refs/heads/main.tar.gz" \
  | tar -xz --strip-components=1 -C "$CODEX_HOME/skills/adversarial-verification"
```

安装或更新后重新启动 Codex；开发时也可以直接将仓库 clone 到同一路径。

## 从 v0.1 升级

原有 `PASS/FAIL/PARTIAL` 终态和 11 套专项 Prompt 已被简洁的需求驱动流程替代。如果有外部自动化依赖旧 verdict 字符串，需要同步调整解析逻辑。独立只读 Verifier、实际证据、根因修复和不允许擅自更改业务语义的原则仍然保留。

MIT License.
