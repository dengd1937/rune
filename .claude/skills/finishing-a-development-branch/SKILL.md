---
name: finishing-a-development-branch
description: "Use when implementation is complete and all tasks have passed review — verifies tests, cleans up docs/plans and artifacts, presents structured integration options (PR/merge/keep/discard), and cleans up workspace. Required after subagent-driven-development skill. Not for use when tests fail or review has open issues."
---

# Finishing a Development Branch

实现完成后的收尾工作流。验证质量 → 清理产物 → 呈现集成选项 → 执行并清理工作区。

**核心原则：** 验证测试 → 清理产物 → 环境检测 → 呈现选项 → 执行 → 工作区清理

**启动时公告：** "使用 finishing-a-development-branch skill 完成收尾工作。"

---

## Step 1：预条件验证

**在呈现选项前，验证实现质量：**

```bash
# 运行项目测试套件
npm test / pytest / go test ./... / cargo test
```

**检查清单：**

- [ ] 测试覆盖率 >= 80%
- [ ] 无残留调试产物（console.log、debugger、print 语句）
- [ ] Phase 3 全局审查已 APPROVE
- [ ] 每个 implementer 的 commit 符合 Conventional Commits

**测试失败：**

```
测试失败（N 个失败）。必须修复后才能继续：

[展示失败信息]

无法继续直到测试通过。
```

**停。不进入 Step 2。**

**测试通过** → 继续 Step 2。

---

## Step 2：文档与产物清理

### 2a. 计划文件清理

```bash
rm docs/plans/<plan-file>
rmdir docs/plans/  # 如果目录为空
```

### 2b. 模块文档

调用 doc-writer agent（模板：`module-doc`）为新模块生成文档。

### 2c. 索引更新

调用 doc-updater agent 更新模块索引和 codemap。

### 2d. Commit 整理

```bash
# 查看当前分支的 commit history
git log --oneline <base-branch>..HEAD
```

如果 implementer 产出了碎片化 commit（如 "wip"、"fix lint"），交互式 squash 为有意义的 Conventional Commits。

调用 commit-quality skill 验证最终 commit 质量。

---

## Step 3：环境检测

**确定工作区状态，决定清理策略：**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

| 状态 | 含义 | 清理策略 |
|------|------|---------|
| `GIT_DIR == GIT_COMMON` | 普通仓库，非 worktree | 无 worktree 需清理 |
| `GIT_DIR != GIT_COMMON`，命名分支 | worktree 开发环境 | 按选项决定是否清理（Step 5） |
| `GIT_DIR != GIT_COMMON`，detached HEAD | 外部管理的 worktree | 不主动清理 |

### 确定基线分支

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

或询问用户："这个分支从 main 分出来的，对吗？"

---

## Step 4：呈现选项

**普通仓库和命名分支 worktree — 4 个选项：**

```
实现完成。接下来：

1. Push 并创建 Pull Request
2. 本地合并回 <base-branch>
3. 保持分支原样（稍后自己处理）
4. 丢弃这个工作

选择？
```

**Detached HEAD（外部管理 workspace）— 3 个选项：**

```
实现完成。当前在 detached HEAD（外部管理的 workspace）。

1. Push 为新分支并创建 Pull Request
2. 保持原样（稍后自己处理）
3. 丢弃这个工作

选择？
```

不附加解释，保持选项简洁。

---

## Step 5：执行选择

### 选项 1：Push 并创建 PR

```bash
# 推送分支
git push -u origin <feature-branch>

# 创建 PR
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets>

## Test plan
- [ ] <verification steps>
EOF
)"
```

**不清理 worktree。** 用户可能需要迭代 PR 反馈。

### 选项 2：本地合并

```bash
# 切到主仓库
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
cd "$MAIN_ROOT"

# 合并
git checkout <base-branch>
git pull
git merge <feature-branch>

# 验证合并后测试通过
<test command>
```

**合并成功后** → Step 6 清理 worktree → 删除分支：

```bash
git branch -d <feature-branch>
```

### 选项 3：保持原样

报告：

```
保持分支 <name>。Worktree 位于 <path>。
```

**不清理 worktree。**

### 选项 4：丢弃

**先确认：**

```
这将永久删除：
- 分支 <name>
- 所有 commit：<commit-list>
- Worktree 位于 <path>

输入 'discard' 确认。
```

等待用户输入 "discard" 后执行。

确认后 → Step 6 清理 worktree → 强制删除分支：

```bash
git branch -D <feature-branch>
```

---

## Step 6：工作区清理

**仅选项 2（合并）和选项 4（丢弃）触发。** 选项 1（PR）和选项 3（保持）始终保留 worktree。

### 普通仓库（`GIT_DIR == GIT_COMMON`）

无 worktree 需清理。完成。

### Worktree

```bash
MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
WORKTREE_PATH=$(git rev-parse --show-toplevel)
```

**安全操作顺序（不可逆，必须严格按序）：**

1. **先 `cd` 到主仓库根目录**（从 worktree 内部执行 `git worktree remove` 会失败）
2. **移除 worktree**
3. **修剪过期注册**
4. **最后删除分支**（worktree 仍引用分支时 `git branch -d` 会失败）

```bash
cd "$MAIN_ROOT"
git worktree remove "$WORKTREE_PATH"
git worktree prune
# 分支删除已在 Step 5 对应选项中执行
```

**溯源判断：** 只移除由 Meridian 流程创建的 worktree（路径在 `.claude/worktrees/` 下）。外部管理的 workspace 不主动清理。

---

## 快速参考

| 选项 | 合并 | Push | 保留 Worktree | 清理分支 |
|------|------|------|---------------|---------|
| 1. PR | - | yes | yes | - |
| 2. 合并 | yes | - | - | yes |
| 3. 保持 | - | - | yes | - |
| 4. 丢弃 | - | - | - | yes (force) |

---

## 常见错误

| 错误 | 后果 | 预防 |
|------|------|------|
| 跳过测试验证 | 合并破坏的代码 / 创建失败的 PR | 始终在选项前验证测试 |
| 开放式提问 | "接下来做什么？" 含义不明 | 呈现恰好 4 个结构化选项 |
| PR 后清理 worktree | 用户无法迭代 PR 反馈 | 仅选项 2/4 清理 |
| 删分支前未移 worktree | `git branch -d` 失败 | 先移 worktree，再删分支 |
| 在 worktree 内部执行 remove | 命令静默失败 | 始终先 `cd` 到主仓库根 |
| 清理外部 workspace | 破坏宿主环境状态 | 只清理 `.claude/worktrees/` 下的路径 |
| 丢弃无需确认 | 误删工作 | 要求输入 "discard" |

---

## Red Flags

**NEVER：**
- 测试未通过时继续
- 未验证合并结果就删除分支
- 未经确认丢弃工作
- 未经请求 force-push
- 合并成功前移除 worktree
- 清理非 Meridian 创建的 worktree
- 从 worktree 内部执行 `git worktree remove`
- 选项 1/3 清理 worktree

**ALWAYS：**
- 选项前验证测试
- 选项前检测环境
- 呈现恰好 4 个选项（detached HEAD 为 3 个）
- 选项 4 要求输入确认
- 选项 2/4 才清理 worktree
- `cd` 到主仓库后再 worktree remove
- worktree remove 后执行 prune
