---
name: task-driven-development
description: 标准开发流程的执行引擎。按任务粒度执行 TDD + 审查循环。
---

# 任务驱动开发

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

## Phase 0：环境就绪检查

从计划的"Environment Prerequisites"段读取依赖清单，逐项验证：

1. 执行每项的 **Verify** 命令，收集结果
2. 全部通过 → 进入 Phase 1
3. 有失败 → 列出失败项 + 错误输出 + 计划中的 Suggested Fix → 阻塞等待用户手动处理 → 用户确认后重验 → 全部通过才继续

**不自动执行 Fix 命令。环境准备是用户的责任。**

---

## Phase 1：加载与校验

1. 读取计划文件（`docs/plans/`）
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

## Phase 2：逐任务执行循环

对每个任务顺序执行以下步骤：

### Step 1：调度 implementer subagent

读取 `implementer-prompt.md` 模板，将 `{{TASK_TEXT}}` 替换为当前任务完整文本后，通过 **`Task(subagent_type="general-purpose")`** 调度。

**模型选择（在 Task 的 model 参数中指定）：**

| 判断条件 | 模型 |
|---------|------|
| 1-2 个文件 + 完整规格（无歧义） | haiku |
| 多文件集成 / 需要跨模块协调 | sonnet |
| 架构判断 / 复杂设计决策 | opus |

**上下文隔离：** 不让 subagent 读计划文件，所有信息通过 prompt 传递。

**注：** 不再调度 `tdd-guide` named agent。tdd-guide.md 已标记废弃，仅作历史向后兼容。

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

### Step 3：规格合规审查

读取 `spec-reviewer-prompt.md` 模板，替换占位符后通过 **`Task(subagent_type="general-purpose", model="sonnet")`** 调度：

- `{{TASK_TEXT}}` → 当前任务完整文本
- `{{IMPLEMENTER_REPORT}}` → Step 1 的 implementer 状态报告
- `{{DIFF}}` → 实施后未 commit 时用 `git diff HEAD`（包含工作区 + 暂存区的所有未 commit 改动）；commit 后用 `git diff HEAD~1`

**通过**（结论 ✅）→ Step 4。

**未通过**（结论 ❌）→ 将审查反馈 + 任务文本构造为新 prompt，重新调度 **implementer subagent**（general-purpose + implementer-prompt.md）修复 → 修复完成后回到 Step 2 重新质量门控和审查。

**修复者是 implementer subagent，不是主代理。主代理不读完整审查反馈后自己改代码。**

**简化复审条件**：如果修复满足以下全部条件，可跳过完整复审，直接确认修复满足 reviewer 反馈即进 Step 4 / Step 6：
1. 修复内容完全采纳 reviewer 反馈，无引申
2. 无超范围改动（仅改 reviewer 指出的位置）
3. 修复 implementer 报告 DONE 且明确说明"未引入额外内容"

不满足以上任一条件 → 必须走完整复审。

### Step 4：代码质量审查

规格合规审查通过后，**在同一消息内并行派发**以下 Task 调用：

**必选（通用质量）：**
读取 `code-quality-reviewer-prompt.md` 模板，替换占位符后，通过 `Task(subagent_type="general-purpose", model="opus")` 调度。
不再调度 `code-reviewer` named agent（已废弃）。

`{{DIFF}}` 来源同 Step 3：未 commit 时用 `git diff HEAD`，commit 后用 `git diff HEAD~1`。
`{{BASE_SHA}}` / `{{HEAD_SHA}}`：未 commit 时填 `HEAD` / `working`；commit 后填实际 hash。

**按语言/场景条件触发（与通用质量并发）：**

| 条件 | 调度 |
|------|------|
| 涉及认证 / 用户输入 / 支付 / DB 查询 | `security-reviewer` named agent |
| 含 `.py` 文件改动 | `python-reviewer` named agent |
| 含 `.ts` / `.tsx` 文件改动 | `typescript-reviewer` named agent |

以上审查互相独立（read-only），并发执行，收集所有结果后统一判定。

**判定规则（二态，无中间状态）：**

| reviewer 输出 | 处置 |
|---|---|
| 所有 reviewer 都 **APPROVE** | → Step 5 |
| 任一 reviewer **BLOCK**（含任意 CRITICAL 或 HIGH） | → 转 implementer subagent 修复 → 回到 Step 2 |

**HIGH = BLOCK 是有意收紧。** task-driven-development 是 AI 自动化流程，没有人类把关，所以 HIGH 必须修。这与 `.claude/rules/code-review.md` 中保留 "HIGH = 警告"的人类 PR 语义并行存在 —— 后者用于人类 PR 审查，前者用于 AI 流程内门控，二者不冲突。

**修复者是 implementer subagent，不是主代理。**

### Step 5：门控判定

Step 3 + Step 4 全部通过 → Step 6 Commit。
任一未通过 → 反馈已在 Step 3/Step 4 转回 implementer subagent；待修复完成后重新从 Step 2 开始。

### Step 6：Commit

调用 `/commit-quality` skill 提交当前任务。commit 后 → 下一任务。

---

## Phase 3：整体审查

所有任务完成后，通过 `Task(subagent_type="general-purpose", model="opus")` + `code-quality-reviewer-prompt.md` 模板做整体审查：任务间集成一致性、遗漏的全局性问题。

---

## Phase 4：最终确认

- [ ] 测试覆盖率 >= 80%
- [ ] 无残留调试产物
- [ ] commit 符合 Conventional Commits
- [ ] docs/plans/ 已清理

---

## 反逃避机制

**NEVER：** 跳过任务 TDD 循环 / 跳过质量门控 / 合并多任务审查 / 审查未通过就下一任务 / 让子代理读计划文件 / 自行判定"太简单不需要 TDD" / 批量写测试或批量实现

**修复者是 implementer subagent，不是主代理。** 主代理不得在收到审查反馈后自己修改代码。

**不再使用 tdd-guide / code-reviewer named agent。** Step 1 / Step 4 通用质量审查统一通过 `Task(general-purpose) + 对应 prompt 模板` 调度。

**Red Flags：** 跳过审查的理由是"改动小" / 多任务合并审查 / 子代理状态不明确 / 先实现后补测试 / 问题标记为"后续处理"

→ 出现任何 Red Flag → 停止，当前任务重新开始。

---

## 模型选择

| 步骤 | 模型 | 备注 |
|------|------|------|
| Step 1 implementer（简单） | haiku | 1-2 文件 + 完整规格（general-purpose） |
| Step 1 implementer（标准） | sonnet | 多文件集成（general-purpose） |
| Step 1 implementer（架构） | opus | 需要架构判断（general-purpose） |
| Step 3 规格合规审查 | sonnet | general-purpose |
| Step 4 通用质量审查 | opus | general-purpose |
| Step 4 专项审查 | sonnet | named agent（security/python/ts） |
| Phase 3 整体审查 | opus | general-purpose（同 Step 4 通用质量） |

---

## 无子代理时的回退

主会话顺序执行每任务 TDD 循环（参考 implementer-prompt.md 的 TDD 执行链）：写测试 → RED → 实现 → GREEN → 重构 → 质量门控 → 内联代码审查（参考 code-quality-reviewer-prompt.md 的检查清单）→ commit。逐任务串行，不跳跃。

---

## 关键原则

- **隔离**：每任务独立上下文（fresh subagent）
- **串行**：任务间严格顺序
- **并发审查**：Step 4 同一消息内并行多个 reviewer
- **门控**：每任务必须通过 TDD + 质量门控 + 双段审查
- **当场修复**：审查问题不拖延，修复闭环始终通过 implementer subagent
- **持续执行**：任务间不询问"是否继续"
