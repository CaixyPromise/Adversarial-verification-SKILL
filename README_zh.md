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

**最多 3 个，不是必须用满 3 个。** 在 4–5 分时，如存在第三类独立且重要的风险，也可以派发第 3 个 Agent。对于鉴权、资金、隐私、数据完整性和不可逆操作，即使改动只有几行，也必须提高审查强度。无法明确的关键业务规则，不允许 AI 擅自猜测并据此改代码；应优先从证据中澄清或请人类决策，**不能只因为不确定就增加 Agent 数量**。

## 三个审查职责及技术思路

- **A — 需求正确性**：独立还原需求与验收行为，沿入口、业务决策、状态变化、持久化及副作用推演，核查遗漏、业务不变量和错误语义。
- **B — 实现一致性与合理复用**：相关变更中审查文件职责、模块内聚与耦合、目录碎片化和稳定命名，防止把临时需求讨论或方案阶段写进文件名；**不以文件行数或数量强制拆分或合并**。按**当前模块 → 直接调用和依赖 → 相关共享实现 → 必要的 Git 历史**逐步检索，证据充分即可停止。比较现有与历史实现的业务语义、重复决策及契约；已有相同能力优先复用，同模块重复优先考虑局部提取。只有多个模块持续需要同一稳定的**通用技术能力**时，才考虑建设有明确归属的工具库；共享业务规则应由领域 Service/Policy 管理，而不是堆进通用 Utils。**不为复用而复用，也不为少量重复代码强制抽象。**
- **C — 系统级工程审查**：按实际风险检查性能、安全、资源生命周期、历史维护约束、部署兼容性，并在涉及分布式业务时审查并发、幂等、超时重试、部分失败、数据一致性和恢复能力。

**1 个 Agent**：按风险覆盖 A+B+C；**2 个 Agent**：默认 A 与 B+C 分工，可按主要风险调整，父 Agent 补足遗漏；**3 个 Agent**：分别承担 A/B/C。不能只是三个 Agent 重复阅读同一份 Diff，也不能因为发现可复用代码就强制进行抽象。具体审查路径见 `references/review-playbook.md`。

无子 Agent 可用时，允许主 Agent 自行按同样原则检查，但需说明不具备独立性。

## 结果与停止条件

- `READY`：必要的检查覆盖充分，已审查范围内没有已知阻塞问题。
- `CHANGES_NEEDED`：仍有证据充分的阻塞性缺陷。
- `NEEDS_DECISION`：核心业务判断需要人类决定。
- `PARTIAL`：部分必要验证无法完成，说明原因和残余风险。

Verifier 必须**先根据原始需求和可信契约独立推导预期行为**，再评价实现，不能把开发 Agent 的实现说明当作正确答案。必要时对比变更前基线与变更后行为，区分**本次引入、原有问题加剧、历史遗留、归因未知**；与当前改动无关的历史问题单独记录，不擅自扩大修复范围，重大历史安全或数据风险仍需升级报告。

每条阻塞问题要有：违反的需求或约束、触发条件、代码或运行证据、实际影响和修复方向。改善建议、设计偏好和待验证假设不能直接当作阻塞缺陷。

默认只做**一轮覆盖式 Review**，修复后**定向复核**。同一个阻塞问题两次修复复核仍失败时，停止自动循环并报告原因，不能为了输出 READY 继续盲改。READY 也不意味着代码绝对无 Bug 或得到生产发布授权。

## 可选的本地审查报告

需要审查归档或成本统计时，使用 `scripts/review_report.py`（详见 [报告使用说明](references/reporting.md)）。**同一个需求只有一对 JSON/HTML 报告，多轮 Review 复用并累积记录**。Reviewer 记录问题证据及修复 Proposal；主 Agent 在实际修改后填写 Fix 和复核结果。纯静态 HTML 支持搜索、严重程度/状态/归因筛选、展开、轮次历史、打印及 JSON 导出，不启动服务。

开始/结束时间由脚本记录，Token 只有拿到可信来源才填写；不把未知当 0。优先使用本地既有的同类报告目录，否则创建专用目录，加入本地 Git `.git/info/exclude`，禁止默认提交归档。报告模块是**按需能力，不阻塞 Review 交付**。

## CLI 命令与更新 Skill

无需第三方依赖，Python 3.9+ 即可使用。安装 Skill 后，在 Skill 目录执行：

```bash
python3 scripts/av.py install-cli  # 在 ~/.local/bin 安装 av 命令
av version
av report start --task-id ISSUE-123 --task "权限包克隆" --risk 5 --agents 2
av report finding --task-id ISSUE-123 --title "权限校验缺失" --proposal "在服务层校验归属"
av report finish --task-id ISSUE-123 --assessment CHANGES_NEEDED

av check-update       # 立即检查 GitHub 最新版本
av update             # 手动确认并更新 Skill
av update --yes       # 明确允许非交互更新
```

如果 `~/.local/bin` 不在 `PATH`，可直接使用 `python3 /Skill目录/scripts/av.py`；审查其他工程时，将 `--project /工程路径` 放在 `report` 前。Windows 可直接使用 Python 运行脚本。原 `scripts/review_report.py` 命令继续兼容，已有报告不会被重新创建。

**非阻塞版本检查**：执行报告 CLI 时先读取本地缓存的更新提示，最多每 24 小时后台请求一次 GitHub 的公开版本清单；短命令通常会在**下一次执行**看到提示，不会等待网络。缓存位于 `~/.cache/adversarial-verification/update-check.json`（或 `$XDG_CACHE_HOME`），这是隐藏的用户级缓存，不放在工程仓库。网络不可用不会阻塞审查。可设置 `AV_DISABLE_UPDATE_CHECK=1` 禁用；不会上传代码、报告或 Token 数据。

**更新必须主动执行**：`av update` 会核对 GitHub 的固定提交和版本清单、安全提取归档、先暂存再替换，并保留旧 Skill 备份。不会自动升级，不会改动项目中的本地审查档案；如果 Skill 本身是 Git 工作区，则拒绝覆盖并要求使用 `git pull`。更新后重新启动 Coding Agent 以载入新指令。

**工件与实现清洁度：** 不将已否决的讨论方案写进最终界面文案或文件名，也不为证明遵守否定式需求而增加不必要的技术开关、包装或分支；保留真正需要的兼容、审计与安全信息。

## 文件结构

- `SKILL.md`：唯一核心执行规则与 Agent 分配策略。
- `references/review-playbook.md`：A/B/C 角色审查思路与按需使用的技术验证方法。
- `references/engineering-quality.md`：通用工程质量原则。
- `references/project-conventions.md`：先理解 AGENTS.md、CLAUDE.md、语言与项目规则。
- `references/code-structure-governance.md`：文件职责、目录组织、过大或过碎模块、命名清洁度与安全重构依据。
- `references/data-access-practices.md`：数据库、N+1、索引、事务、死锁、缓存与一致性。
- `references/frontend-experience.md`：复用既有设计系统与组件、交互简洁、用户可懂的文案；页面不能残留 AI 会话中的已否决方案。
- `references/security-review-checklist.md`：安全敏感需求可选参考。
- `agents/openai.yaml`：Agent 展示与默认指令。
- `scripts/av.py`、`skill-version.json`：CLI、异步版本检查缓存与显式更新。
- `scripts/review_report.py`、`templates/review-report.html`：兼容原命令的静态报告生成脚本与模板。
- `references/reporting.md`：命令、同任务归档复用、数据来源与 Git 安全说明。

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
