# 安装与更新指南 / Installation Guide

本指南适用于 **Adversarial Verification Skill v0.3.1+**，覆盖 Windows、macOS、Linux、首次安装、CLI 安装、更新、回滚及卸载。本 Skill 不需要运行 Web 服务，CLI 仅依赖 **Python 3.9+ 标准库**。请仅从官方仓库下载：

- 源代码：<https://github.com/CaixyPromise/Adversarial-verification-SKILL>
- 核心文件：`SKILL.md` 位于仓库**根目录**，不是 `skills/adversarial-verification/` 子目录。
- 默认安装位置：Codex `~/.codex/skills/adversarial-verification`（Windows 为 `%USERPROFILE%\.codex\skills\adversarial-verification`）。
- CLI：`av`。CLI 安装的是一个小型启动器；不会复制第二份 Skill。

> 安装前建议先检查目标目录是否已有 Skill。**不要直接覆盖已有目录**，尤其是手动修改过的文件。已有版本的升级方式见本文“更新与回滚”。

## 1. Windows 10/11 — PowerShell 安装（推荐）

**准备：** 安装 [Python 3.9+](https://www.python.org/downloads/windows/)。在 PowerShell 中确认：

~~~powershell
py -3 --version
~~~

若 `py` 不可用，可以改用 `python --version`，并将下面的 `py -3` 替换为 `python`。CLI 不依赖 Git、Node.js 或 pip。建议在**普通用户权限**的 PowerShell 中操作，无需管理员权限。

### 1.1 下载并安装 Skill

把下面整段粘贴到 PowerShell 执行。脚本使用系统临时目录，下载完成后安装到 Codex 的用户目录，不在业务工程目录生成报告或脚本。

~~~powershell
$repo = 'CaixyPromise/Adversarial-verification-SKILL'
$skillDir = Join-Path $HOME '.codex\skills\adversarial-verification'

# 避免覆盖已有安装或用户定制的内容
if (Test-Path -LiteralPath $skillDir) {
    throw "目录已存在：$skillDir。已有安装请使用 av update；Git 克隆请使用 git pull。"
}

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("av-install-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    $zipPath = Join-Path $tempDir 'skill.zip'
    $url = "https://github.com/$repo/archive/refs/heads/main.zip"
    Invoke-WebRequest -Uri $url -OutFile $zipPath
    Expand-Archive -LiteralPath $zipPath -DestinationPath $tempDir -Force

    $source = Join-Path $tempDir 'Adversarial-verification-SKILL-main'
    if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) {
        throw "下载文件缺少 SKILL.md；安装已中止。"
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $skillDir) -Force | Out-Null
    Move-Item -LiteralPath $source -Destination $skillDir
}
finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

py -3 (Join-Path $skillDir 'scripts\av.py') version
~~~

如果最后输出版本号，说明 Skill 已安装到磁盘。Codex 需要重新启动后才会重新加载该 Skill。

### 1.2 安装 Windows `av` 命令

v0.3.1 起，`install-cli` 可生成 Windows 的 `av.cmd` 启动器：

~~~powershell
$skillDir = Join-Path $HOME '.codex\skills\adversarial-verification'
py -3 (Join-Path $skillDir 'scripts\av.py') install-cli
~~~

默认启动器位于 `$HOME\.local\bin\av.cmd`。**以下命令只修改当前用户 PATH，不需要管理员权限：**

~~~powershell
$bin = Join-Path $HOME '.local\bin'
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$entries = @($userPath -split ';' | Where-Object { $_ })

if ($entries -notcontains $bin) {
    [Environment]::SetEnvironmentVariable('Path', (($entries + $bin) -join ';'), 'User')
}

# 让当前 PowerShell 窗口立即生效
if (($env:Path -split ';') -notcontains $bin) {
    $env:Path += ";$bin"
}

av version
av check-update
~~~

之后新开的 PowerShell 或 Windows Terminal 也可直接使用 `av`。如果没有添加 PATH，仍然可以使用 `py -3 (Join-Path $skillDir 'scripts\av.py') ...`。

**如果提示 `av` 不是命令：** 在新 PowerShell 窗口运行 `Get-Command av`；确认 `$HOME\.local\bin\av.cmd` 存在并在用户 PATH 中。若 `py -3` 不存在，请使用实际可运行的 Python 命令重新执行 `install-cli`。

### 1.3 Windows 使用示例

~~~powershell
av version
av check-update
av update          # 需要人工确认；不会静默安装
av update --yes    # 明确允许非交互更新

# 注意：--project 放在 report 前
av --project 'C:\Projects\Example' report start --task-id ISSUE-123 --task '权限包克隆' --risk 5 --agents 2
av --project 'C:\Projects\Example' report finding --task-id ISSUE-123 --title '权限归属校验缺失' --severity high --evidence '服务层缺少归属判断' --proposal '在服务层校验对象归属'
av --project 'C:\Projects\Example' report finish --task-id ISSUE-123 --assessment CHANGES_NEEDED
~~~

同一个 `--task-id` 的多轮 Review 会复用同一个 JSON/HTML 报告。若只想查看/生成报告而不检查远程版本，可设置 `$env:AV_DISABLE_UPDATE_CHECK = '1'`。

## 2. macOS / Linux — 安装

确认 `python3 --version` 显示 Python 3.9 或更高，且已安装 `curl`、`tar`。

~~~bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILL_DIR="$CODEX_HOME/skills/adversarial-verification"

# 不覆盖已经存在的 Skill
if [ -e "$SKILL_DIR" ]; then
  echo "已有安装：$SKILL_DIR；请使用 av update 或 git pull" >&2
else
  mkdir -p "$SKILL_DIR"
  curl -fL "https://github.com/CaixyPromise/Adversarial-verification-SKILL/archive/refs/heads/main.tar.gz" \
    | tar -xz --strip-components=1 -C "$SKILL_DIR"
fi

python3 "$SKILL_DIR/scripts/av.py" version
python3 "$SKILL_DIR/scripts/av.py" install-cli
~~~

默认命令入口安装到 `~/.local/bin/av`。如果 `av` 找不到，在当前终端执行：

~~~bash
export PATH="$HOME/.local/bin:$PATH"
av version
~~~

要永久生效，将上述 `export PATH=...` 加入当前 shell 的启动配置（如 `~/.zshrc` 或 `~/.bashrc`），重新打开终端。之后可使用 `av report ...`、`av check-update`、`av update`。

如果 `curl` 失败或解压中断，请先核实目标目录中是否存在完整 `SKILL.md` 和 `scripts/av.py`，不要继续使用残缺安装。

## 3. 不装启动器：直接运行 CLI

安装 Skill 后，`av` **不是强制依赖**。可以始终使用：

| 平台 | 示例 |
| --- | --- |
| Windows PowerShell | `py -3 "$HOME\.codex\skills\adversarial-verification\scripts\av.py" version` |
| macOS / Linux | `python3 "$HOME/.codex/skills/adversarial-verification/scripts/av.py" version` |

如果 `CODEX_HOME` 自定义，请使用实际安装路径替换默认目录。

## 4. 更新、备份与回滚

### 4.1 普通压缩包安装（推荐）

~~~text
av version
av check-update
av update
~~~

- `check-update` **立即联网**读取 GitHub 的公开版本信息并更新本地缓存。
- 日常 `av report` 最多每 24 小时启动一次**非阻塞后台版本检查**，下一次运行时提示可更新版本。可通过 `AV_DISABLE_UPDATE_CHECK=1` 禁用。
- `av update` **不是自动更新**：确认后从 GitHub 固定提交下载、核对版本清单、安全解包、暂存并替换 Skill，同时保留旧版本在同级 `.av-backup-...` 文件夹。
- `av update --yes` 用于用户明确授权的非交互场景；`av update --force` 仅用于重新安装同一版本。
- 如果本地 Skill 是 Git 工作区，`av update` 会拒绝覆盖它；请改用 `git pull --ff-only`。
- 更新后重启 Codex / Coding Agent。项目内的 JSON/HTML Review 报告不受更新影响。

**回滚：** 先退出使用 Skill 的 Coding Agent，将当前 Skill 目录移走，再把同级 `.av-backup-...` 中需要恢复的那一个目录恢复为 `adversarial-verification`。不要删除尚未确认可用的备份。报告存储在目标业务项目中，通常无需迁移。

**v0.2.x 老版本（没有 CLI）：** 先将旧 Skill 安装目录重命名备份，再按照本文对应系统的“首次安装”步骤安装新版；请勿直接在旧目录叠加文件。安装新版后再使用 `av update`。

### 4.2 Git 克隆安装

如果您通过 `git clone` 将仓库直接放在 Codex Skills 目录，应在安装目录执行：

~~~bash
git pull --ff-only
~~~

Windows PowerShell 示例：

~~~powershell
git -C "$HOME\.codex\skills\adversarial-verification" pull --ff-only
~~~

此方式保留 Git 的正常版本管理，`av update` 会明确拒绝对该工作区做目录级替换。更新后如启动器已经安装，`av.cmd` 或 `av` 仍指向原有 Skill 路径。

## 5. 报告文件与隐私

- JSON 和静态 HTML 默认保存在**被审查项目**的 `.adversarial-verification/reports/`；如果该项目有旧版 Skill 的有效归档目录，会优先复用。
- 同一个稳定 `--task-id` 的不同轮次复用同一个报告，不创建多个平行档案。
- 报告目录加入所在 Git 仓库的本地 `.git/info/exclude`，**不是可提交的 `.gitignore`**；若不安全，脚本会拒绝写入。
- 版本缓存存放在用户级 `~/.cache/adversarial-verification/update-check.json`（Windows 为 `$HOME\.cache\adversarial-verification\update-check.json`，亦支持 `XDG_CACHE_HOME`）。
- 后台网络检查只请求 GitHub 的公开版本信息，不上传项目代码、报告、Prompt 或 Token 记录。
- Token 数据仅在有可信来源时记录，缺失时保持未知。

## 6. 卸载（可选）

**Windows PowerShell**（确认路径无误后执行）：

~~~powershell
Remove-Item -LiteralPath (Join-Path $HOME '.codex\skills\adversarial-verification') -Recurse -Force
Remove-Item -LiteralPath (Join-Path $HOME '.local\bin\av.cmd') -Force -ErrorAction SilentlyContinue
~~~

**macOS / Linux**：

~~~bash
rm -rf "$HOME/.codex/skills/adversarial-verification"
rm -f "$HOME/.local/bin/av"
~~~

如自定义了 Skill 目录，请相应调整。卸载不会自动删除业务项目中的报告和旧版本备份。用户 PATH 中的 `~/.local/bin` 可保留供其他 CLI 使用。

## 7. 常见问题

| 症状 | 处理 |
| --- | --- |
| `py` / `python` 找不到 | 安装 Python 3.9+；Windows 可使用 `py -3` 或 `python` |
| `av` 未识别 | 先确认 `av.cmd` / `av` 已生成，再将 `~/.local/bin` 加到 PATH |
| `av update` 提示 Git 工作区 | 用 `git pull --ff-only`，不要让自动更新覆盖本地 Git 状态 |
| 更新检查失败 / GitHub 不可访问 | 不影响本地报告；稍后用 `av check-update` 重试 |
| Skill 已安装但 Agent 无法识别 | 检查安装目录根部存在 `SKILL.md`，然后重启 Agent |
| 更新后希望恢复旧版 | 使用 CLI 留下的 `.av-backup-...` 目录回滚 |
| 报告变成多份 | 后续 Review 使用相同 `--task-id`，不要依赖不同任务标题或不同分支名识别同一需求 |
| Windows PowerShell 下载失败 | 检查 HTTPS 网络访问及 Python；不要随意执行来源不明的安装脚本 |

---

## English quick reference

1. Windows: install Python 3.9+, run the **PowerShell** installation block in §1.1, then `py -3 "$HOME\.codex\skills\adversarial-verification\scripts\av.py" install-cli`; add `$HOME\.local\bin` to the user PATH (see §1.2).
2. macOS/Linux: install Python 3.9+, follow §2, then add `~/.local/bin` to your PATH.
3. Commands: `av version`, `av report ...`, `av check-update`, `av update`. Updating is never automatic.
4. Git-clone installs should use `git pull --ff-only`, not `av update`. Review archives stay local and are not uploaded.
