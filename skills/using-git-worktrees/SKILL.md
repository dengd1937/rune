---
name: using-git-worktrees
description: Use when starting subagent-driven-development (Phase 0a) or before executing implementation plans — ensures an isolated workspace exists. Detects existing isolation first, prefers native worktree tools, falls back to `git worktree add` under .claude/worktrees/.
origin: rune
---

# Using Git Worktrees

## Overview

确保工作发生在隔离工作区。优先用平台原生 worktree 工具，仅当无原生工具时回落 `git worktree add`。

**核心原则：** 先检测已有隔离 → 再用原生工具 → 最后才回落 git worktree。永远不和宿主对抗。

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

---

## Step 0：检测已有隔离

**创建任何东西前，先检查当前是否已在隔离工作区内。**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**子模块守卫：** `GIT_DIR != GIT_COMMON` 在 git 子模块中也成立。在断定"已在 worktree"前，先验证不是子模块：

```bash
# 返回非空路径 → 在子模块，按普通仓库处理
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**若 `GIT_DIR != GIT_COMMON` 且非子模块：** 已在 linked worktree。**跳过创建**，直接到 Step 2（项目就绪）。

报告（携带分支状态）：
- 在命名分支上："Already in isolated workspace at `<path>` on branch `<name>`."
- Detached HEAD："Already in isolated workspace at `<path>` (detached HEAD, externally managed). Branch creation needed at finish time."

**若 `GIT_DIR == GIT_COMMON` 或在子模块：** 在普通仓库 checkout。

用户是否已在指令中声明 worktree 偏好？如未声明，先请求同意：

> "Would you like me to set up an isolated worktree? It protects your current branch from changes."

已声明的偏好直接遵循，不再询问。用户拒绝则在原地工作，跳到 Step 2。

---

## Step 1：创建隔离工作区

**有两种机制，按顺序尝试。**

### 1a. 原生 worktree 工具（优先）

用户已同意建 worktree（Step 0）。你是否已经有原生工具？可能名为 `EnterWorktree` / `WorktreeCreate` / `/worktree` 命令 / `--worktree` 标志 / Agent tool 的 `isolation: "worktree"` 参数。若有，使用它并跳到 Step 2。

原生工具自动处理目录放置、分支创建和清理。当你有原生工具时还用 `git worktree add` 会创建宿主看不见也管不了的幻影状态。

**仅当无原生工具时**，进入 Step 1b。

### 1b. Git worktree 回落

**仅当 Step 1a 不适用时使用** —— 没有原生 worktree 工具，手动用 git 创建。

#### 目录约定

Rune 统一使用：

```
<repo-root>/.claude/worktrees/<branch-name>/
```

例：
- `feature/auth` 分支 → `.claude/worktrees/feature-auth/`
- `hotfix/login-null` 分支 → `.claude/worktrees/hotfix-login-null/`

分支名中的 `/` 替换为 `-`。

#### 安全验证（必须）

`.claude/worktrees/` **必须**在 `.gitignore` 中，避免 worktree 内容被误提交：

```bash
git check-ignore -q .claude/worktrees
```

**未被 ignore：** 添加到 `.gitignore`，commit 该变更，然后继续。

#### 创建 worktree

```bash
# 命名：分支名中的 / 替换为 -
SAFE_BRANCH=$(echo "$BRANCH_NAME" | tr '/' '-')
WORKTREE_PATH=".claude/worktrees/$SAFE_BRANCH"

# 新建分支同时建 worktree
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME"

# 或检出已有分支
git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"

cd "$WORKTREE_PATH"
```

**Sandbox 回落：** 若 `git worktree add` 因权限/沙箱失败，告知用户沙箱阻止了 worktree 创建，将在当前目录工作。然后在原地完成 setup 和 baseline 测试。

---

## Step 2：项目就绪

自动检测并运行对应 setup：

```bash
# Python (Rune 默认)
if [ -f pyproject.toml ]; then uv sync; fi

# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

---

## Step 3：验证 Baseline

跑测试套件确认起点干净：

```bash
# 使用项目对应命令
pytest / npm test / cargo test / go test ./...
```

**测试失败：** **立即阻塞**，报告失败用例，等用户确认（是修复 baseline 还是允许带病继续）。**不要自行决定继续。**

**测试通过：** 报告就绪。

### 报告格式

```
Worktree ready at <full-path>
Baseline tests passing (<N> tests, 0 failures)
Ready to execute plan: <plan-file-or-feature-name>
```

---

## Quick Reference

| 情况 | 处理 |
|------|------|
| 已在 linked worktree | 跳过创建（Step 0） |
| 在子模块 | 按普通仓库处理（Step 0 守卫） |
| 有原生 worktree 工具 | 使用它（Step 1a） |
| 无原生工具 | git worktree 回落（Step 1b） |
| `.claude/worktrees/` 未被 ignore | 添加到 .gitignore + commit |
| 分支名含 `/` | 替换为 `-` 用作目录名 |
| 权限错误 | Sandbox 回落，原地工作 |
| Baseline 测试失败 | 立即阻塞，等用户确认 |
| 项目无 pyproject/package | 跳过依赖安装 |

---

## Common Mistakes

### 和宿主对抗

- **问题：** 平台已提供隔离时还用 `git worktree add`
- **修复：** Step 0 检测已有隔离，Step 1a 让位给原生工具

### 跳过检测

- **问题：** 在已存在的 worktree 内再建嵌套 worktree
- **修复：** 任何创建前总是先跑 Step 0

### 跳过 ignore 验证

- **问题：** worktree 内容被 git 追踪，污染 git status
- **修复：** 项目本地 worktree 前总是 `git check-ignore` 验证

### 使用旧 sibling 约定

- **问题：** 用 `../.worktrees/<repo>-<branch>` 这种 sibling 路径
- **修复：** 已废弃。Rune 统一用 `.claude/worktrees/<branch-name>/`（项目内 + 与 finishing skill 对齐）

### Baseline 失败时继续

- **问题：** 无法区分新 bug 和已有问题
- **修复：** 立即阻塞，要用户明确许可才继续

---

## Red Flags

**Never：**
- Step 0 检测到已有隔离时仍创建新 worktree
- 有原生工具（如 `EnterWorktree` / Agent `isolation: "worktree"`）时还用 `git worktree add` —— **头号错误**
- 跳过 Step 1a 直接跳到 Step 1b
- 未验证 ignore 就在项目本地创建 worktree
- 跳过 baseline 测试验证
- Baseline 失败不询问就继续

**Always：**
- 先跑 Step 0 检测
- 优先原生工具
- 路径用 `.claude/worktrees/<branch-name>/`
- 验证已被 ignore
- 自动检测并运行项目 setup
- 验证 baseline 测试通过

---

## 与其他 skill 的集成

- **被调用者：** `subagent-driven-development` (Phase 0a)、单文件降级路径在动手前
- **清理由：** `finishing-a-development-branch` (Step 6) 凭路径溯源 `.claude/worktrees/` 触发
