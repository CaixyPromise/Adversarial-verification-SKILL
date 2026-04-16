# adversarial-verification

一个面向 Agentic Coding 工作流的“对抗式验证”技能。

这个SKILL受 Claude Code 的 adversarial verification / verifier agent 机制启发，并在这里被重新打包成一个可独立复用的 skill，供其他 coding agent 使用。

English version: [`README.md`](./README.md)

这个 skill 的目标，是强制把以下三类角色清晰拆开：

- 负责实现的实现代理
- 负责找问题的独立 verifier 子代理
- 在 verifier 失败后必须按根因修复、不能乱补丁的父代理 / 主线程

核心思想很简单：

- verifier 不是来确认“看起来大概没问题”的
- verifier 是来故意尝试把改动搞坏、找出薄弱点的
- 主线程不能为了变绿而迎合样例、歪曲业务、放宽约束或乱打补丁

## 这个 skill 适合解决什么问题

当你希望 AI Coding 工作流在“非 trivial 改动”后，增加一道更强的软件质量门时，就适合用这个 skill。

尤其适合这些场景：

- 后端与 API 改动
- 需要运行时交互验证的前端流程
- 数据库与迁移改动
- Shell、CLI、脚本、自动化流程
- 安全敏感路径
- 性能或规模敏感改动
- 数据管道与异步任务
- 移动端或桌面客户端行为
- 基础设施、部署、运维类改动
- LLM / Agent 工作流改动

## 包含哪些内容

- `SKILL.md`：技能主入口
- `agents/openai.yaml`：agent 配置骨架
- `references/playbook.md`：对抗式探测打法
- `references/domain-checklists.md`：性能、数据库、内存、安全、业务正确性、反作弊等评审域
- `references/prompt-templates.md`：按改动类型拆分的 verifier prompt 模板
- `references/parent-workflow.md`：parent agent -> verifier subagent 工作流
- `references/security-review-checklist.md`：结构化安全评审 checklist
- `references/root-cause-fix-policy.md`：主线程在 verifier `FAIL` 后如何做根因修复
- `references/main-thread-discipline.md`：主线程禁止样例迎合、浅层补丁、越权自作主张的约束

## 在 Codex 中安装

这个 skill 的目录结构已经按可独立安装到 Codex 本地 skill 目录的方式整理好了，默认目标目录为：

```text
~/.codex/skills/adversarial-verification
```

安装后需要重启 Codex，才能加载新的 skill。

### 方案一：通过 GitHub 直接 `curl` 安装

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_HOME/skills"

curl -L "https://github.com/CaixyPromise/Adversarial-verification-SKILL/archive/refs/heads/main.tar.gz" \
  | tar -xz --strip-components=2 -C "$CODEX_HOME/skills" \
      "Adversarial-verification-SKILL-main/skills/adversarial-verification"
```

### 方案二：通过 Codex 的 `skill-installer` 安装

本地已经有 Codex 自带的 `skill-installer`，也可以按它的 GitHub repo/path 安装方式来装：

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo CaixyPromise/Adversarial-verification-SKILL \
  --path skills/adversarial-verification
```

如果希望安装方式尽量轻量、不要依赖额外 helper script，那么上面的 `curl` 方案更直接。

## 设计原则

这个 skill 明确内置了几条强约束：

- 验证必须独立于实现
- 测试通过只是上下文，不是最终证明
- 只测 happy path 不够
- verifier 必须主动尝试搞坏系统
- 主线程必须修根因，不能修表象
- 行为语义有歧义时，必须升级给用户确认，而不是自己猜

## verifier 的 verdict 契约

verifier 最终必须只给出以下三种结论之一：

- `VERDICT: PASS`
- `VERDICT: FAIL`
- `VERDICT: PARTIAL`

而且 verifier 必须给“证据”，不是给“感觉”：

- 跑了什么命令
- 实际观察到了什么输出
- 预期和实际有什么差异
- 每个检查项的明确结果

## 已支持的专项 verifier prompt

目前已经覆盖：

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

## 使用示例

### 1. 由父代理拉起 verifier 子代理

推荐在实现完成后、且工作属于 non-trivial 的情况下使用。

示例 parent -> verifier prompt：

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

### 2. verifier 的基本工作流

verifier 应该做的事情：

1. 读取项目说明和运行命令
2. 在适用时运行 build / test / lint / typecheck
3. 直接运行被改动的功能
4. 至少执行一个对抗式探测
5. 检查真实输出、运行时行为和副作用
6. 给出带证据的 verdict

### 3. 主线程在 `FAIL` 之后应该怎么做

parent / main thread 应该：

1. 把 `FAIL` 当成交付阻塞，而不是可协商意见
2. 先读 `references/main-thread-discipline.md`
3. 再读 `references/root-cause-fix-policy.md`
4. 直接复现失败
5. 原因不清楚时先加临时日志或诊断
6. 以业务/功能根因为目标来修
7. 行为存在歧义时先问用户
8. 修完后重新做验证

## 安全类评审怎么用

对于安全敏感改动，推荐这样搭配：

- 使用 `security/penetration` 专项 verifier prompt
- 配合 `references/security-review-checklist.md`
- 先报告已确认的最高风险问题
- 如果确认存在 `Critical` 或 `High` 问题，不允许给出 `PASS`

## 许可证

MIT，详见 `LICENSE`。
