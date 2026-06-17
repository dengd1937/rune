---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task, before touching code. Creates a task-level implementation plan saved to docs/plans/. User approval required before implementation."
---

# Writing Plans

Create task-level implementation plans for multi-step development work. Plans are the execution input for the `subagent-driven-development` skill.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `docs/plans/<feature-name>.md`

**Context：** writing-plans 阶段本身**不创建** worktree。如果实现阶段需要隔离工作区，由 `subagent-driven-development` 在 Phase 0a 调用 `using-git-worktrees` 完成。计划文件应在 worktree 创建前已 commit 到当前分支，便于 worktree 内可见。

---

## Scope Check

If the work involves any of the following, stop and suggest the user run `/brainstorm` first to produce capability spec(s):

- New modules / new dependencies / new database tables
- Data model changes or migrations
- Changes affecting >= 2 existing modules
- Technical selection with no precedent in existing ADRs
- Module boundary issues emerging during refactoring

Capability spec(s) produced, writing-plans treats brainstorm Phase 4 的技术设计（方案选择 / 架构 / 数据模型 / API）与 capability spec 的行为作为输入约束。It focuses on **how to implement**, not **which path to choose**.

If the spec covers multiple independent subsystems, suggest breaking into separate plans — one per subsystem.

---

## Planning Process

### 1. Requirement Analysis

**前序产物验证：** brainstorm 的 capability mapping 指明本 feature 触及哪些 capability spec（`docs/specs/<capability>-spec.md`）。确认以下产物存在：

```
capability specs = docs/specs/<capability>-spec.md（brainstorm 写/改的，≥1 个）
designs          = docs/designs/{feature}/（如经过 design-workflow）
```

capability spec 不存在 → 报告用户（应先跑 brainstorm），不继续。feature 名称确定后，计划文件写入 `docs/plans/{feature}.md`。**本计划吸收 brainstorm Phase 4 的技术设计**（方案/架构/数据模型/API）到「架构变更」段；行为真相引用相关 capability specs。

- Fully understand feature requirements from spec or user input
- Ask clarifying questions when necessary
- Identify success criteria
- List assumptions and constraints

### 2. Architecture Review

- Analyze existing codebase structure
- Identify affected components
- Review patterns in similar implementations
- Consider reusable solutions
- Locked-version API check — for every third-party API the plan references, read the project's lock/manifest (uv.lock / package-lock / go.mod etc.) and confirm the symbol exists in the **locked** version, not the latest. If absent, switch to an approach available in the locked version; never carry a version assumption into implementation

### 3. File Structure

Before defining tasks, map out which files will be created or modified:

- Design units with clear boundaries and well-defined interfaces
- Files that change together should live together
- In existing codebases, follow established patterns
- Prefer smaller, focused files over large ones

### 4. Task Decomposition

- Each task: 1-3 files
- Each task has independent test strategy
- Each task passes through per-task execution gates independently
- Sort by dependency priority, group related changes, minimize context switching

### Prohibited Patterns

- "Implement all API endpoints" as a single task
- Tasks spanning 3+ files
- "Unified testing" or "unified review" steps

---

## Plan Document Format

```markdown
# 实现计划：[功能名称]

## 执行方式

本计划通过 `/subagent-driven-development` skill 执行。以下任务描述是 skill 的输入规格，不是直接执行指令。

## 概述
[2-3 句摘要]

## 需求
- [需求 1]
- [需求 2]

## 架构变更
- [变更 1：文件路径及描述]
- [变更 2：文件路径及描述]

## 环境前置（Environment Prerequisites）

列出计划中运行测试所需的每个外部依赖。扫描项目中的：测试运行器配置、docker-compose 服务、.env.example 条目、ORM/数据库配置，以及测试套件依赖的其他服务。对找到的每个依赖项提供：

- **[依赖名称]**：[描述]
  - 验证：`[就绪时退出码为 0 的命令]`
  - 修复：`[使其就绪的命令]`

若项目除测试运行器外无外部依赖，仅列出测试运行器。不要虚构项目未使用的依赖。

## 实现步骤

### 阶段 1：[阶段名称]
1. **[步骤名称]**（文件：path/to/file.ts）
   - 操作：具体操作
   - 理由：此步骤的原因
   - 依赖：无 / 依赖步骤 X
   - 风险：低/中/高

### 阶段 2：[阶段名称]
...

## 测试策略
- 单元测试：[需测试的文件]
- 集成测试：[需测试的流程]
- 端到端测试：[需测试的用户旅程]

## E2E 稳定性要求
- 所有 E2E 测试必须使用幂等设置（每个测试创建并清理自己的数据）
- 禁止依赖共享 fixture 或其他测试的残留数据
- 不稳定的测试用 `test.fixme()` 隔离
- 使用 `data-testid` locator，不用 CSS/XPath
- 使用 `waitForResponse()` / `waitForSelector()`，不用 `waitForTimeout()`
- 配置 `trace: 'on-first-retry'`

## 风险与缓解
- **风险**：[描述]
  - 缓解：[应对措施]

## 验收标准
- [ ] 标准 1
- [ ] 标准 2

## 已审定决策（可选）

仅当 Plan Review dual-review 确认了"有意偏离"时，由 writing-plans 写入此段（见「结果聚合」——此段是唯一合法写入点）。每条只记决策与理由，**不写**"因此 reviewer 不要报 X"式免责措辞。

- **决策点**：[具体决策，如"依赖 X 锁 ≤2.1，不升级"]
  - 审定结论：[dual-review 确认这是有意选择]
  - 有意理由：[为什么这样选]
```

### Task Template

每个任务必须遵循以下模板：

```markdown
### 任务 N：[具体操作]

**文件：** 新建/修改 + 测试路径
**测试规格：** 需覆盖的场景和预期行为（由 implementer subagent 编写具体测试用例）
**验证标准：** GREEN 条件（描述通过标准，非具体命令）
**审查要求：** 需通过的审查类型（code-quality-reviewer / python-reviewer / typescript-reviewer 等 prompt 模板）
```

---

## No Placeholders

每个任务必须包含实施者所需的具体信息。以下模式是**计划失败**——绝不写入：

- "TBD"、"TODO"、"implement later"、"fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"（未说明具体处理什么）
- "Write tests for the above"（未指定测试什么场景和预期行为）
- "Similar to Task N"（重复规格描述——implementer 可能不按顺序读取任务）
- 只描述"做什么"而不说明"怎么做"的步骤
- 引用未在任何任务中定义的类型、函数或方法

---

## Self-Review

完成完整计划后，运行以下自检清单——这不是 subagent 派发，而是自身校验：

**1. Spec coverage（规格覆盖）**：浏览相关 capability spec(s) 中的每个 Requirement / Scenario。能找到实现它的任务吗？列出任何缺口。

**2. Placeholder scan（占位符扫描）**：搜索计划中的 red flags——"No Placeholders" 一节中列出的任何模式。发现就修复。

**3. Type consistency（类型一致性）**：后续任务中使用的类型、方法签名、属性名是否与先前任务中的定义一致？Task 3 中叫 `clearLayers()` 的函数在 Task 7 中变成了 `clearFullLayers()` 就是 bug。

发现问题则就地修复。发现 spec 需求没有对应任务则补充任务。

---

## Plan Review (Dual Subagent)

自检通过后，**在同一消息内并行派发**两个独立 reviewer：

### Reviewer 1: Document Quality

```
Agent tool (general-purpose):
  description: "Review plan document quality"
  prompt: |
    [使用 plan-reviewer-prompt.md 模板]
    - Plan file: docs/plans/<feature>.md
    - Capability specs: docs/specs/<capability>-spec.md（brainstorm mapping 指明的，如存在）
```

检查文档完整性、spec 对齐、任务拆分、占位符、可构建性、类型一致性。

### Reviewer 2: Technical Risk

```
Agent tool (general-purpose, model="opus"):
  description: "Technical risk review of plan"
  prompt: |
    [使用 technical-risk-reviewer-prompt.md 模板]
    - Plan file: docs/plans/<feature>.md
    - Capability specs: docs/specs/<capability>-spec.md（brainstorm mapping 指明的，如存在）
```

对抗性技术风险分析：架构合理性、实现可行性、测试策略深度、性能风险、scope 挑战、失败模式。

### 结果聚合

**两个 reviewer 都 Approved →** 计划通过；若 review 过程中 reviewer 提出某决策但经判定为**有意保留**，由 writing-plans 将其写入 plan 的「已审定决策」段——**此段唯一合法写入点；controller / implementer / 运行时一律不得追加**。然后进入 Execution Handoff。

**任一 reviewer 发现 Issues →** 修复问题 → 重新运行自检清单 → 重新派发两个 reviewer。

---

## Per-Task Execution Gate

以下三道门控由 `subagent-driven-development` skill 在执行时自动管理，计划中只需在每个任务的"审查要求"中指定审查类型：

1. **TDD** — RED→GREEN→IMPROVE 循环完成
2. **Quality Gate** — 格式化 / lint / 类型检查通过
3. **Code Review** — code-quality-reviewer 通过（规格合规 + 代码质量）

---

## Execution Handoff

计划执行编排由 `subagent-driven-development` skill 负责。skill 会：

- 通过 Agent tool 调度 implementer subagent（隔离上下文）
- 将完整任务文本粘贴到 prompt 中；不让 subagent 读取计划文件
- subagent 报告状态后，skill 决定下一步（DONE → 审查，BLOCKED → 拆分或补充上下文）
- 逐任务串行执行，每任务通过三道门控

---

## Scale & Staging

功能较大时，拆分为可独立交付的阶段：

- **阶段 1**：最小可用 — 能提供价值的最小切片
- **阶段 2**：核心体验 — 完整的主路径
- **阶段 3**：边界情况 — 错误处理、边界情况、打磨
- **阶段 4**：优化 — 性能、监控、分析

每个阶段应可独立合并。避免所有阶段全部完成才能工作的计划。

