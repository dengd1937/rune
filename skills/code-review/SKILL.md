---
name: code-review
description: Use after implementation (bug fix or feature task) to dispatch appropriate reviewers and return binary APPROVE/BLOCK verdict. Shared by investigate and subagent-driven-development.
---

# Code Review

实现完成后的审查调度。接收 diff + 上下文，派发合适的 reviewer，返回二态判定。

**启动时公告：** "使用 code-review skill 调度审查。"

---

## 两种模式

### 模式 A：per-task review

逐任务审查。用于 SDD Phase 2 或 investigate Phase 5。

**输入：**
- `task_text` — 任务规格文本（可选；无 task_text 时跳过 spec review）
- `diff` — `git diff <base_SHA>..<head_SHA>` 输出
- `base_SHA` / `head_SHA` — 审查范围
- `implementer_report` — implementer 的状态报告（可选，传给 spec-reviewer）

**派发规则：**

| 条件 | 派发 |
|------|------|
| 必选（每次） | `Task(general-purpose, model="opus")` + `code-quality-reviewer-prompt.md` |
| 有 task_text | `Task(general-purpose, model="sonnet")` + `spec-reviewer-prompt.md` |
| diff 含 `.py` 文件 | `Task(general-purpose, model="sonnet")` + `python-reviewer-prompt.md` |
| diff 含 `.ts` / `.tsx` 文件 | `Task(general-purpose, model="sonnet")` + `typescript-reviewer-prompt.md` |

**注意：** 安全审查已合并进 `code-quality-reviewer-prompt.md`（OWASP Top 10 + 安全模式表），不再单独派发。

**所有 reviewer 在同一消息内并发派发。** 互不依赖（只读），收集所有结果后统一判定。

**模板占位符替换：**

spec-reviewer-prompt.md：
- `{{TASK_TEXT}}` → task_text
- `{{IMPLEMENTER_REPORT}}` → implementer_report
- `{{DIFF}}` → diff

code-quality-reviewer-prompt.md：
- `{{TASK_TEXT}}` → task_text
- `{{DIFF}}` → diff
- `{{BASE_SHA}}` / `{{HEAD_SHA}}` → base_SHA / head_SHA

python-reviewer-prompt.md：
- `{{DIFF}}` → diff
- `{{BASE_SHA}}` / `{{HEAD_SHA}}` → base_SHA / head_SHA

typescript-reviewer-prompt.md：
- `{{DIFF}}` → diff
- `{{BASE_SHA}}` / `{{HEAD_SHA}}` → base_SHA / head_SHA

### 模式 B：global review

跨任务全局审查。用于 SDD Phase 3（多任务场景）。

**输入：**
- `plan_text` — 完整计划文本（所有任务）
- `task_summaries` — 每个任务的 implementer 状态报告摘要
- `full_diff` — `git diff <first_base_SHA>..<last_head_SHA>` 全量 diff
- `base_SHA` / `head_SHA` — 全局审查范围

**派发：** `Task(general-purpose, model="opus")` + `global-reviewer-prompt.md`

**模板占位符替换：**

global-reviewer-prompt.md：
- `{{PLAN_TEXT}}` → plan_text
- `{{TASK_SUMMARIES}}` → task_summaries
- `{{DIFF}}` → full_diff
- `{{BASE_SHA}}` / `{{HEAD_SHA}}` → base_SHA / head_SHA

---

## 派发自检（聚合判定前必做）

收齐 reviewer 结果、进入「判定规则」之前，核对实际派发是否符合派发规则：

1. 按本次 diff 特征推导**应派发集合**：
   - `code-quality-reviewer`（必选）
   - 有 task_text → + `spec-reviewer`
   - diff 含 `.py` → + `python-reviewer`
   - diff 含 `.ts` / `.tsx` → + `typescript-reviewer`
2. 与**实际派发集合**比对
3. 不一致 → 列出缺失 reviewer + 缺失理由，**不得静默进入聚合**；补齐派发，或由用户显式确认降级后方可继续

**长任务序列专项**：应派发集合只由 diff 特征决定，**不随任务序号变化，不因"提速 / 避免 cold-start"在中段把多个 reviewer 简并为单个"综合 reviewer"**。每个 per-task review 独立推导，前一任务怎么派发不构成本任务的依据。这是 SDD「Controller 传递契约 · 派发集合不随序列漂移」的执行机制。

---

## 判定规则

**模板负责检查清单**（什么是好代码、什么是坏代码）。

**code-review skill 负责判定逻辑**（severity → verdict 映射 + 多 reviewer 聚合）。

### severity → verdict 映射

| 严重程度 | verdict | 说明 |
|---------|---------|------|
| CRITICAL | BLOCK | 安全漏洞、数据丢失、功能缺失 |
| HIGH | BLOCK | 自动化流程收紧——无人类把关，宁严勿宽 |
| MEDIUM | 不阻塞 | 记录但不阻塞 |
| LOW | 不阻塞 | 记录但不阻塞 |

HIGH = BLOCK 是**有意收紧**：AI 自动化场景没有人类把关，HIGH 必须修。这与人类 PR 审查中"HIGH = 警告"的语义并行存在——后者用于人类 PR 审查，前者用于 AI 流程内门控，二者不冲突。

### 多 reviewer 聚合

| 条件 | 结果 |
|------|------|
| 所有 reviewer 都 APPROVE | APPROVE |
| 任一 reviewer BLOCK | BLOCK（附合并后的反馈） |

---

## 输出

**APPROVE：**
```
审查通过。无 CRITICAL 或 HIGH 问题。
[MEDIUM/LOW 问题如有，列于此供参考]
```

**BLOCK：**
```
审查未通过。以下问题必须修复：

[按 blocking → simple → complex 排序]
[每条附 file:line + fix 建议]

修复后重新运行 code-review。
```

---

## 调用者集成

### subagent-driven-development

```
Phase 2 Step 3: /code-review (per-task)
  BLOCK → /review-handling → implementer 修复 → 回 Step 2 质量门控

Phase 3: /code-review (global)
  BLOCK → /review-handling → implementer 修复 → 重 Phase 3
```

### investigate

```
Phase 5: /code-review (per-task, task_text=根因报告)
  BLOCK → /review-handling → 修复 → 重跑质量门控 + /code-review
  APPROVE → finishing-a-development-branch
```

---

## 模型选择

| 派发 | 模型 | 备注 |
|------|------|------|
| code-quality-reviewer | opus | general-purpose，含安全审查 |
| spec-reviewer | sonnet | general-purpose |
| python-reviewer | sonnet | general-purpose + prompt 模板 |
| typescript-reviewer | sonnet | general-purpose + prompt 模板 |
| global-reviewer | opus | general-purpose |

---

## Red Flags

**NEVER：**
- 跳过审查因为"改动小"
- 合并多任务审查
- reviewer 结果未到就判定
- 只跑部分 reviewer 或把多个 reviewer 简并为单个"综合 reviewer"（按派发规则全跑，不简并）
- 长任务序列中段改变派发策略
- 忽略 HIGH 问题标记为"可以接受"

**ALWAYS：**
- 按派发规则检查所有条件
- 同一消息内并发派发
- 等所有 reviewer 返回后聚合
- 聚合判定前做派发自检
- 严格按 severity→verdict 映射判定
