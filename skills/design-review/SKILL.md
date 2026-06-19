---
name: design-review
description: "Use when reaching the design-workflow V2-4 hard gate — adversarially reviews design artifacts (token coverage, contract completeness, artifact consistency, accessibility docs, responsive coverage, DESIGN.md compliance) against docs/designs/<feature>/ before development handoff."
---

# Design Review

设计产物移交开发前的对抗式审查（design-workflow V2-4 hard gate）。派 `Task(general-purpose, model="sonnet")` 独立审查——独立上下文 = fresh eyes，没参与做设计、不被锚定。承接 V2-4 hard gate：未通过（block）不进入 Gate 3。

**启动时公告：** "使用 design-review skill 对设计产物做对抗式审查。"

---

## 派发

**输入：**
- `feature_dir` — 设计产物根目录（如 `docs/designs/<feature>/`）

**派发：** `Task(general-purpose, model="sonnet")` + [reviewer-prompt.md](reviewer-prompt.md)（`{{FEATURE_DIR}}` → feature_dir）。

reviewer 只读文件系统、不调 Pencil MCP、不分析 PNG（视觉质量由人类审查 + dev Step 3 Playwright 覆盖）。产出 6 维评分 + 详细发现 + failure modes + verdict，**不写文件**——verdict 由主对话在用户审批后写 `review-verdict.md`（经 doc-ops write 模板 `review-verdict`）。

---

## Verdict 语义

| Verdict | 含义 | 后续 |
|---|---|---|
| **approve** | 无 CRITICAL，HIGH 有清晰缓解 | 可进 Gate 3 用户审批 |
| **needs-attention** | 有 HIGH 需用户决策 | 停，用户决策后回 V2-3 或继续 |
| **block** | 有 CRITICAL | 必须修，重跑 V2-4 |

**block = 不进 Gate 3**（hard gate）。

---

## 模型选择

| 派发 | 模型 | 备注 |
|------|------|------|
| design-reviewer | sonnet | general-purpose，对抗式审查 |

---

## Red Flags

**NEVER：**
- 因"改动小"跳过审查
- 让 reviewer 写文件（它只读 + 返回 verdict）
- 视觉质量交给 reviewer（它无法分析 PNG；视觉由人类 + Playwright 覆盖）
- block 后不经修复直接进 Gate 3

**ALWAYS：**
- 用独立 subagent（fresh eyes），不在主对话内联自审
- 等 verdict 返回后再判定 gate
- DESIGN.md 不存在时该维 N/A，不扣分
