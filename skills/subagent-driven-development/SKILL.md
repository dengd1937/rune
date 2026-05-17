---
name: subagent-driven-development
description: "Use when executing implementation plans with independent tasks. Dispatches a fresh subagent per task with TDD + quality gate + code review. Required after writing-plans skill. Terminal state: invokes finishing-a-development-branch skill."
---

# Subagent 驱动开发

标准开发流程的执行引擎。非降级场景默认使用。

---

## 持续执行原则

任务间**不停下来询问"是否继续"**。完成一个任务后立即进入下一个。

允许停下的三种情况：
1. **BLOCKED**：遇到无法独立解决的阻塞，需用户介入
2. **真正的歧义**：任务意图不明确，继续会导致方向性错误
3. **全部任务完成**：计划中所有任务均已通过门控

其他情况一律持续执行。

---

## Phase 0a：工作区隔离（建议）

**调用 `using-git-worktrees` skill**，确保实现工作发生在隔离工作区：

- 已在 linked worktree → skill 自动检测并跳过创建
- 在主仓库 → skill 询问用户是否建 worktree（路径 `.claude/worktrees/<branch>/`）
- 用户拒绝 → 在原地继续

**这不是 IRON LAW，是工程建议。** 用户可拒绝。但默认应建议建。

skill 同时负责 baseline 测试验证；baseline 失败时由 skill 阻塞，控制权交回用户。

完成后进入 Phase 0。

---

## Phase 0：环境就绪检查

从计划的"Environment Prerequisites"段读取依赖清单，逐项验证：

1. 执行每项的 **Verify** 命令，收集结果
2. 全部通过 → 进入 Phase 1
3. 有失败 → 列出失败项 + 错误输出 + 计划中的 Suggested Fix → 阻塞等待用户手动处理 → 用户确认后重验 → 全部通过才继续

**不自动执行 Fix 命令。环境准备是用户的责任。**

---

## Phase 1：加载与校验

1. 读取计划文件（`docs/plans/`，由 writing-plans skill 产出）
2. 提取所有任务文本
3. 检查粒度：每任务 1-3 文件，有独立 TDD 步骤和审查门控
4. 如果任务涉及 UI，实现前确认计划已引用：
   - `DESIGN.md`（如存在）
   - `docs/designs/<feature>/review-verdict.md`
   - `docs/designs/<feature>/tokens/`
   - `docs/designs/<feature>/components/*.md`
   - 已记录的 design identity gap 及其用户决策
5. 不合格 → 报告用户，建议重新拆分

---

## Controller 传递契约

SDD 精确约束了 implementer 能做什么（见 implementer-prompt），但 controller 把任务交出去时同样受契约约束。controller 违约不会被 implementer-prompt 自动拦截——这是 controller 自身纪律。

### 不变量 1：传规格，不传实现

调度 implementer（Phase 2 Step 1）时，`{{TASK_TEXT}}` 替换内容及任何附加上下文：

| 可传 | 不可传 |
|------|--------|
| 任务规格、验收标准、GREEN 条件 | 可直接誊抄的完整函数体 / 实现源码 |
| 接口签名、数据结构契约、类型定义 | 逐行实现指令（"把这段代码写进去"） |
| 测试场景、必测边界、依赖说明 | 任何绕过 RED→GREEN 的现成答案 |

**理由**：implementer 必须靠 RED→GREEN 自行设计。controller 把实现喂进 prompt → implementer 退化为誊写工 → TDD 设计发现价值归零 → code-review 也查不出设计问题（设计未经独立检验，是 controller 单方拍定）。

判据：接口签名/数据契约是"做什么"的边界，可传；函数体是"怎么做"的答案，不可传。

---

## Phase 2：逐任务执行循环

对每个任务顺序执行以下步骤：

**记录起点：** `base_SHA = $(git rev-parse HEAD)`，用于后续 diff 计算和审查范围。

### Step 1：调度 implementer subagent

读取 `implementer-prompt.md` 模板，将 `{{TASK_TEXT}}` 替换为当前任务完整文本后，通过 **`Task(subagent_type="general-purpose")`** 调度。替换内容与任何附加上下文必须遵守 Controller 传递契约不变量 1（传规格不传实现）。

**模型选择（在 Task 的 model 参数中指定）：**

| 判断条件 | 模型 |
|---------|------|
| 1-2 个文件 + 完整规格（无歧义） | haiku |
| 多文件集成 / 需要跨模块协调 | sonnet |
| 架构判断 / 复杂设计决策 | opus |

**上下文隔离：** 不让 subagent 读计划文件，所有信息通过 prompt 传递。

**提问处理：**

如果 implementer 在开始工作前提问（通过 NEEDS_CONTEXT 或显式提问）→ Controller 回答问题 → 重新调度（fresh subagent，携带原始任务文本 + 回答）。

不要忽略提问。提问说明信息不足，强行执行会导致方向性错误。

**状态处理：**

| 状态 | 处理 |
|------|------|
| DONE | → Step 2 |
| DONE_WITH_CONCERNS | 记录关注点 → Step 2 |
| BLOCKED | 报告用户，拆分任务或补充上下文 |
| NEEDS_CONTEXT | 补充信息，重新调度（fresh subagent） |

### Step 2：质量门控

调用 `/code-quality-gate` skill：格式化 → lint → 类型检查 → debug 产物检测。

**通过** → Step 3。

**失败处理：**
- 将「质量门控错误输出 + 当前任务文本」构造为新 prompt
- 重新调度 **新的 implementer subagent（同样 general-purpose + implementer-prompt.md）** 修复（使用与 Step 1 相同的模型）
- 修复完成后重跑 Step 2
- **主代理不自己读完整错误输出后改代码**

### Step 3：代码审查

调用 `/code-review` (per-task)：
- `task_text` = 当前任务完整文本
- `diff` = `git diff <base_SHA>`（包含未提交的工作区变更）
- `base_SHA` / `head_SHA` = Phase 2 起点记录的 `base_SHA` + 当前 `HEAD`
- `implementer_report` = Step 1 的 implementer 状态报告

**APPROVE** → Step 4。

**BLOCK** → 调用 `/review-handling` 处理反馈 → 构造修复 prompt → 重新调度 implementer subagent 修复 → 修复完成后回到 Step 2。

**修复者是 implementer subagent，不是主代理。主代理不读审查反馈后自己改代码。**

### Step 4：门控判定 + 提交

**审查通过：**
1. 将工作区变更 commit（Conventional Commits 格式，scope + description 从任务描述提取）
2. 记录新的 `head_SHA`
3. 标记任务完成 → 下一任务

**未通过：** 反馈已在 Step 3 转回 implementer subagent；待修复完成后重新从 Step 2 开始。

---

## Phase 3：全局审查

所有任务通过 Phase 2 后，调用 `/code-review` (global)：
- `plan_text` = 完整计划文本（所有任务）
- `task_summaries` = 每个任务的 implementer 状态报告摘要（DONE / DONE_WITH_CONCERNS + 关键决策）
- `full_diff` = `git diff <first_base_SHA>..HEAD`
- `base_SHA` = 第一个任务的 base_SHA
- `head_SHA` = HEAD

**APPROVE** → Phase 4。

**BLOCK** → 调用 `/review-handling` 处理反馈 → 构造修复 prompt → 重新调度 implementer subagent 修复 → 修复完成后重新 Phase 3。

**修复者是 implementer subagent，不是主代理。**

---

## Phase 4：收尾

Phase 3 通过后，调用 `/finishing-a-development-branch` skill：验证测试 → 文档与产物清理 → commit 整理 → 环境检测 → 呈现集成选项 → 执行并清理工作区。

---

## 反逃避机制

**NEVER：** 跳过任务 TDD 循环 / 跳过质量门控 / 合并多任务审查 / 审查未通过就下一任务 / 让子代理读计划文件 / 自行判定"太简单不需要 TDD" / 批量写测试或批量实现 / 在 implementer prompt 中放入可直接誊抄的完整实现（违反传递契约不变量 1）

**修复者是 implementer subagent，不是主代理。** 主代理不得在收到审查反馈后自己修改代码。

**Red Flags：** 跳过审查的理由是"改动小" / 多任务合并审查 / 子代理状态不明确 / 先实现后补测试 / 问题标记为"后续处理"

→ 出现任何 Red Flag → 停止，当前任务重新开始。

---

## 模型选择

| 步骤 | 模型 | 备注 |
|------|------|------|
| Step 1 implementer（简单） | haiku | 1-2 文件 + 完整规格（general-purpose） |
| Step 1 implementer（标准） | sonnet | 多文件集成（general-purpose） |
| Step 1 implementer（架构） | opus | 需要架构判断（general-purpose） |
| Step 3 代码审查 | 见 code-review skill | 派发规则和模型选择由 code-review skill 管理 |
| Phase 3 全局审查 | 见 code-review skill | 同上 |

---

## 无子代理时的回退

主会话顺序执行每任务 TDD 循环（参考 implementer-prompt.md 的 TDD 执行链）：写测试 → RED → 实现 → GREEN → 重构 → 质量门控 → 调用 `/code-review` (per-task) → 审查通过后 commit。逐任务串行，不跳跃。

---

## 关键原则

- **隔离**：每任务独立上下文（fresh subagent）
- **串行**：任务间严格顺序
- **审查委托**：代码审查通过 `/code-review` skill 统一调度，不在 SDD 内管理 reviewer 派发
- **门控**：每任务必须通过 TDD + 质量门控 + 代码审查
- **当场修复**：审查问题不拖延，修复闭环始终通过 implementer subagent
- **持续执行**：任务间不询问"是否继续"

---

## Integration

**前置 skill（建议触发）：**
- `using-git-worktrees` —— Phase 0a 调用，确保隔离工作区（已在 worktree 则跳过）

**后继 skill（必触发）：**
- `code-review` —— Phase 2 Step 3 / Phase 3 调度
- `review-handling` —— code-review BLOCK 时
- `finishing-a-development-branch` —— Phase 4 收尾，凭路径溯源清理 `.claude/worktrees/` 下的 worktree
