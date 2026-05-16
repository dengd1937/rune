---
name: feedback
description: "Use when you hit a rune problem worth reporting — a hook false-positive, a skill behaving against its docs, a confusing or bloated workflow step, a misleading doc. Walks through structuring the report and produces a GitHub issue draft for the rune repo. Never submits automatically; you review and run gh issue create yourself."
origin: rune
---

# Feedback

把使用 rune 过程中遇到的问题整理成 GitHub issue 草稿。对话驱动，不读会话历史，不自动提交。

**启动时公告：** "使用 feedback skill 整理 rune 反馈草稿。"

## 严格禁止

- 读取会话 transcript / git log / 用户项目代码
- 在草稿中夹带用户业务代码、文件路径、内部需求、密钥
- 自动执行 `gh issue create` / `git push` / 任何网络写操作
- 默认目标仓库（`dengd1937/rune`）以外的仓库

## 工作流

### Step 1: 问清反馈内容

对话式追问（一次 2-3 个，不一次抛完）：

- 你在用 rune 做什么时遇到的？（场景，抽象描述，**不要贴业务代码**）
- rune 实际做了什么？（现象）
- 你期望它怎么做？（期望）

### Step 1.5: 定位（可选）

如果反馈与某个 rune 工作流环节相关，参照下表帮用户定位是哪个 skill/环节，让 issue 的标题与标签更精准。用户说不清也可跳过。

| 环节 | Skill / 组件 | 典型反馈 |
|------|-------------|---------|
| 产品 / 技术设计 | brainstorm | Scale Gate 误判、Phase 啰嗦或过重 |
| UI 设计 | design-workflow / pencil-design | L1/L2 路由、产物缺失 |
| 实现计划 | writing-plans | 任务拆分、占位符、模板冗余 |
| 逐任务实现 | subagent-driven-development / tdd-workflow | TDD 门控、子代理调度 |
| 根因调查 | investigate | 流程偏离、Hard Gate |
| 代码审查 | code-review / review-handling | reviewer 误报、派发规则 |
| 收尾 | finishing-a-development-branch / doc-sync | 集成选项、worktree 清理、文档对账 |
| 接入存量项目 | onboard | 目录脚手架、Pre-Rune catalog |
| 物理拦截 | hooks/ | 误拦正常命令、secret 扫描误报 |
| 文档 | README / CLAUDE.md / 各 skill 文档 | 表述不清、与实际行为不符 |

### Step 2: 分类

- **bug**：rune 行为与文档不符 / hook 误拦 / skill 描述错误
- **enhancement**：流程优化 / 新场景支持 / 冗余精简
- **docs**：文档表述不清 / README 误导

### Step 3: 生成草稿

```markdown
**Title**: [bug|enhancement|docs]: <短描述>

## Context
<触发场景，抽象描述，不含用户业务内容>

## Observed
<rune 当前行为>

## Expected
<期望行为>

## Suggested Change
<针对 skill/hook/doc 的具体改动建议，可选>

**Repo**: dengd1937/rune
**Labels**: <bug|enhancement|docs>
```

### Step 4: 用户审阅 + 自提

展示完整草稿，要求用户逐条审阅：

- 删掉任何涉及内部信息的句子
- 合并重复建议
- 必要时补复现步骤

可选：草稿暂存到**用户项目本地** `docs/feedback/<date>-<slug>.md`（不是 rune 仓库，由用户决定是否保留）。

告知用户：

> 审阅无误后自行执行：
> `gh issue create --repo dengd1937/rune --title "..." --body-file <file>`
> rune 不会代你提交。

## 不做什么

- 不自动提交 issue
- 不读会话 transcript
- 不夹带用户代码
- 不修改任何代码或配置

## Red Flags

**NEVER：**
- 自动执行 `gh issue create` 或任何网络写操作
- 读取会话 transcript / 用户项目代码塞进草稿
- 在草稿中保留用户业务上下文、路径、密钥
- 向 `dengd1937/rune` 以外的仓库定向

**ALWAYS：**
- 草稿用抽象场景描述，剥离用户业务内容
- 生成后停下让用户逐条审阅
- 由用户自行 `gh issue create` 提交
