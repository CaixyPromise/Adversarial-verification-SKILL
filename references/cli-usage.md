# Review CLI 使用与故障降级

这份文档面向 Coding Agent 和人工审查者。**报告是可选的辅助归档，代码实现、测试和交付是主任务；CLI、导入、HTML 生成或文件写入失败绝不能阻塞主任务，也不能为了修好报告而反复 Review。** 审查本身的真实缺陷仍按 SKILL.md 正常处理。

## 1. 入口、身份和存储

安装 CLI 后使用 \`av\`，或直接调用 \`python3 /path/to/skill/scripts/av.py\`（Windows 用 \`py -3\`）。当工作目录不是被审查项目时，放置全局参数在 \`report\` **之前**：

\`\`\`bash
av --project /path/to/project report start --task-id ISSUE-123 --task "Permission package clone" --risk 5 --agents 2
\`\`\`

同一个需求使用**完全相同的稳定 \`--task-id\`**，无论涉及几轮审查/修复。第一次 \`start\` 会创建任务级 JSON/HTML；重复 \`start\` 复用原档案，已结束轮次之后才创建新轮次。CLI 输出 \`json\` 和 \`html\` 的实际路径，不要根据示例猜测 hash 文件名。

报告优先放入项目中已有的本 Skill 归档目录，否则创建 \`.adversarial-verification/reports/\` 并验证本地 Git exclude。避免随意创建报告目录。JSON 为权威数据；HTML 是从 JSON 派生的静态视图。

## 2. 各命令参数与角色

| 命令 | 核心参数 | 使用者 / 行为 |
| --- | --- | --- |
| \`start\` | \`--task-id\`, 首次 \`--task\`; 可选 \`--risk 0..6\`, \`--agents 0..3\` | 主 Agent；开始/复用报告和轮次 |
| \`finding\` | \`--title\` 必需；\`--id\`, \`--category\`, \`--severity\`, \`--attribution\`, \`--evidence\`, \`--proposal\`, \`--reviewer\` | Reviewer；只记录问题证据与修复建议，不宣称已经修好 |
| \`fix\` | \`--id\` 和 \`--description\` 必需；\`--status\`, \`--verification\`, \`--actor\` | Implementer；实际修复后记录 Fix 和验证结果 |
| \`event\` | \`--text\` 必需，\`--kind\` 可选 | 记录关键测试或决策 |
| \`import\` | \`--file\` 必需，\`--dry-run\` 可选 | 先验证整批 JSON，再一次性写入问题、Fix、事件 |
| \`finish\` | \`--assessment\` 必需；可选 \`--summary\`, \`--input-tokens\`, \`--output-tokens\`, \`--token-source\` | 主 Agent；结束本轮并生成最新报告 |
| \`show\` / \`render\` | \`--task-id\` | 查看归档路径/计数或重新生成 HTML |

所有命令建议显式携带 \`--task-id\`。严重度：\`critical/high/medium/low/info\`；归因：\`introduced/worsened/pre-existing/unknown\`；修复状态：\`open/fixed/verified/wontfix/needs-decision\`。全局命令及安装参见 [INSTALL.md](../INSTALL.md)。

### 单条问题与实际修复

\`\`\`bash
av report finding --task-id ISSUE-123 --title "Missing ownership check" --category authorization --severity high --attribution introduced --reviewer "Agent C" --evidence "PermissionService.java:82 cross-user request bypasses ownership" --proposal "Enforce resource ownership at service boundary"
# 从 CLI 输出得到 finding_id，例如 F001
av report fix --task-id ISSUE-123 --id F001 --status fixed --description "Added service-layer authorization"
av report fix --task-id ISSUE-123 --id F001 --status verified --description "Authorization corrected" --verification "Cross-user negative case and targeted regression suite passed"
av report finish --task-id ISSUE-123 --assessment READY --summary "Necessary verification completed, no known blockers"
\`\`\`

\`fixed\` 表示已修改，\`verified\` 应在真实验证后使用。命令**记录**证据，不会自动运行测试、确认真实修复或自动评估模型用量。Token 仅有真实运行时计数和 \`--token-source\` 时填写，未知保持未知。

## 3. 批量导入：减少 Tool Calls

JSON 文件按以下格式准备（建议放在项目已忽略的报告目录或临时目录，**不要提交包含敏感信息的 JSON 到 Git**）：

\`\`\`json
{
  "schema": "adversarial-verification-import/v1",
  "findings": [
    {
      "key": "ownership",
      "title": "Missing ownership check",
      "category": "authorization",
      "severity": "high",
      "attribution": "introduced",
      "reviewer": "Agent C",
      "evidence": "PermissionService.java:82 allows a cross-user write",
      "proposal": "Enforce ownership in service; add negative test"
    },
    {
      "key": "query-n1",
      "title": "N+1 database queries",
      "category": "performance",
      "severity": "medium",
      "attribution": "worsened",
      "reviewer": "Agent B",
      "evidence": "One child query issued per list row",
      "proposal": "Batch child lookups while preserving result ordering"
    }
  ],
  "fixes": [
    {
      "ref": "ownership",
      "status": "verified",
      "description": "Added ownership validation",
      "verification": "Unauthorized request rejected in integration test",
      "actor": "Implementer"
    }
  ],
  "events": [
    {"kind": "test", "text": "Targeted authorization regression tests completed"}
  ]
}
\`\`\`

\`\`\`bash
av report start --task-id ISSUE-123 --task "Permission package clone" --risk 5 --agents 2
av report import --task-id ISSUE-123 --file /tmp/findings.json --dry-run
av report import --task-id ISSUE-123 --file /tmp/findings.json
\`\`\`

**整批验证、一次保存：** 输入为 UTF-8 JSON，最大 1 MiB、最多 300 条 Finding/Fix/Event 合计。先验证 schema、字段、枚举、引用；发现错误则不修改归档。支持用 \`"key"\` 为同批新问题命名，再用 Fix 的 \`"ref"\` 指向它；也支持通过现有问题 \`"id":"F001"\` 定向更新。后者的 Fix 使用 \`"id":"F001"\`，且 \`id\` 与 \`ref\` 不可同时给出。

重复导入**同一字节内容**到同一审查轮次将跳过重复写入；下一轮重新发现已修复问题会保持同一个 F### 并重新打开。即使提交了同名问题，也不会创建新的平行报告。多次导入修改过的内容不一定幂等，应使用稳定问题 ID，并检查返回的 \`finding_ids\`。

\`--dry-run\` 仅校验并预演，不写入 JSON/HTML；正式导入成功后，CLI 返回记录的 ID、轮次和实际报告路径。CLI 把 \`finding\`、\`fix\` 和 \`event\` 归入同一个活动轮次；先运行 \`start\`，不要在 \`finish\` 后直接追加。

**审查者不可仅因有修复 Proposal 就填写 \`fixes\`。** 只有实现者完成实际修改、复核后才记录真实 Fix。批量导入同时包含新问题和修复时，亦遵循此原则。

## 4. CLI / 写入异常：不得阻碍开发与交付

按以下优先级降级，**不进行无界重试或临时重写报告系统**：

1. 一次 CLI 失败时记录简短原因；如果只是 \`av\` 找不到，尝试一次 \`python3 /path/to/skill/scripts/av.py report ...\` 或原脚本 \`review_report.py\`。
2. 若 CLI、模板或 HTML 写入异常，但**已有任务 JSON 可以安全访问**，可以直接按照下面的字段示例编辑**同一文件**，原始记录不能删除或整体替换。保存前使用临时文件 + \`os.replace\` 的原子写法，并保持 Git 排除。
3. 若 JSON 路径未知、不可读、已被 Git 跟踪、无法安全写入或不能验证格式，**不要另建多个零散的报告目录**。直接在给用户的最终回复中列出发现、证据、Proposal、实际 Fix、测试结果和报告限制。继续正常修复、测试与交付；不能谎称报告已成功归档。

人工修改**已有 JSON** 时，应保留 \`schema\`、\`identity\`、\`task_id\`、\`sessions\`、\`findings\`、已存在的问题 ID 和修复历史。新问题用递增 F###，不要产生重复 ID；同一问题后续修复追加到它的 \`repairs\`。JSON 中的必要字段结构：

\`\`\`json
{
  "schema": "adversarial-verification-report/v1",
  "identity": "id:issue-123",
  "task_id": "ISSUE-123",
  "task": "Permission package clone",
  "project": "example-project",
  "created_at": "2026-11-02T10:00:00+08:00",
  "updated_at": "2026-11-02T11:00:00+08:00",
  "sessions": [
    {
      "round": 1,
      "started_at": "2026-11-02T10:00:00+08:00",
      "ended_at": null,
      "risk_score": 5,
      "agents": 2,
      "assessment": null,
      "summary": "",
      "input_tokens": null,
      "output_tokens": null,
      "token_source": null,
      "events": []
    }
  ],
  "findings": [
    {
      "id": "F001",
      "title": "Missing ownership check",
      "category": "authorization",
      "severity": "high",
      "attribution": "introduced",
      "evidence": "Observed cross-user request",
      "proposal": "Check ownership",
      "reviewer": "Agent C",
      "status": "fixed",
      "first_seen_round": 1,
      "last_seen_round": 1,
      "repairs": [
        {
          "round": 1,
          "at": "2026-11-02T10:30:00+08:00",
          "status": "fixed",
          "description": "Added service ownership check",
          "verification": "",
          "actor": "Implementer"
        }
      ]
    }
  ]
}
\`\`\`

这个 JSON 仅用于**理解当前结构**，不能拿它覆盖已有报告，否则会丢失历史记录。不要凭空补齐时间、Token、问题证据和实际测试结果。

### 直接写入的原子保存方法

当 AI 已在已有报告的原始 JSON 中修改了所需字段，可以用 Python 标准库保证单文件原子替换：

\`\`\`python
from pathlib import Path
import json, os, tempfile

report = Path("/absolute/path/from/earlier-cli-output/review-issue-123-xxxx.json")
if not report.is_file():
    raise RuntimeError("Existing report not found; do not invent a second archive")
original = json.loads(report.read_text(encoding="utf-8"))
assert original["schema"] == "adversarial-verification-report/v1"

# 示例：只更新已经存在的 F001；如果问题不存在，拒绝猜测或重新编号。
finding = next((f for f in original["findings"] if f["id"] == "F001"), None)
if finding is None:
    raise RuntimeError("F001 not found; do not invent a duplicate issue")

finding["evidence"] = "服务层缺少资源归属校验（以实际证据为准）"
finding["proposal"] = "在服务层增加权限归属校验"

# 实际修复后才追加 repairs，不要只凭 Proposal 声称已修复：
# finding["status"] = "fixed"
# finding.setdefault("repairs", []).append({
#     "round": original["sessions"][-1]["round"],
#     "at": "实际修复发生时记录的 ISO 8601 时间",
#     "status": "fixed",
#     "description": "具体执行的修改",
#     "verification": "",
#     "actor": "Implementer"
# })

with tempfile.NamedTemporaryFile("w", encoding="utf-8",
                                 dir=report.parent, delete=False) as stream:
    json.dump(original, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
    temp = Path(stream.name)
try:
    os.replace(temp, report)
finally:
    temp.unlink(missing_ok=True)
\`\`\`

**注意：** 如果仅直接更新 JSON，HTML 不会自动刷新。CLI 恢复后可以对同一 \`--task-id\` 执行 \`av report render\`，重新生成 HTML；若命令仍异常，报告 HTML 可能落后，必须告知用户，不能声称它已同步。

仅允许向**已有且安全的同任务归档**执行这种手动编辑。不要覆盖 Git-tracked 文件，不要为了写报告改变项目源代码/测试、降低 Review 标准，或让报告异常变成 \`CHANGES_NEEDED\` / \`PARTIAL\` 的原因。真正的代码证据不足仍需要如实反映在 Review 结论里。

## 5. 推荐给 Agent 的操作原则

**Reviewer：** 多问题优先批量 \`import --file\`；只写发现和 Proposal。**Implementer：** 完成真实 Fix 后补充 Fix、复核和必要事件。**Parent：** 使用同一需求 ID 汇总、结束并向用户提供结果。出现工具错误时一次降级即可，**继续主任务**；用户能够知道结果比修复一个报告工具更重要。

后台更新检测只是 CLI 的附属能力，与报告写入是否成功无关；GitHub 网络不可用也不能成为暂停开发的理由。
