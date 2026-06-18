---
name: doc-ops
description: "Use when a workflow needs to write a templated documentation artifact (capability spec, change proposal/specs delta, ADR, design intent/component-contract/token-source-map/layout-report/review-verdict, l1 design note) from prepared structured data, or when reconciling doc indexes (FEATURE-CATALOG, CODEMAP) after a workflow step."
---

# Doc Ops

文档机械操作的统一执行器。两种模式：**write**（模板 + 数据 → 写产物）和 **sync**（对账 FEATURE-CATALOG + CODEMAP）。两者都派 `Task(general-purpose, model="haiku")` subagent 执行（机械操作，用 haiku 控成本）。

**启动时公告：** "使用 doc-ops skill 执行文档操作（write / sync）。"

---

## Mode write

调用方已备好结构化数据 + 模板标识符。把数据按模板格式化写入对应文件位置。

**输入：**
- `template` — 模板 ID（见映射表）
- `feature` — feature 名（kebab-case）
- `data` — 结构化数据（JSON 或 markdown）
- `overwrite`（可选）— 是否覆盖已有文件，默认 false

**派发：** `Task(general-purpose, model="haiku")` + [writer-prompt.md](writer-prompt.md) + `templates/<template>.md` + data。

模板映射（template ID → 目标路径 → 来源工作流）见 [writer-prompt.md](writer-prompt.md)。覆盖冲突时 subagent 报告并等待指示（不擅自覆盖）。

---

## Mode sync

工作流完成后，对账共享知识索引与新增产物。

**输入：**
- `scope` — 本次更新范围（哪个段、哪个 feature）

**派发：** `Task(general-purpose, model="haiku")` + [updater-prompt.md](updater-prompt.md) + scope。

对账 FEATURE-CATALOG（Features / Components / Decisions 三段，含 Status 状态机）与 CODEMAP（目录结构 + 关键模块表含「Capability Spec」列 + 数据流 + 外部依赖）。README 不在机械对账范围（人读叙述文档，定期手动维护）。

---

## 模型选择

| 模式 | 模型 | 备注 |
|------|------|------|
| write | haiku | general-purpose，机械格式化 |
| sync | haiku | general-purpose，机械对账 |

---

## Red Flags

**NEVER：**
- write 模式下自行决定内容或做研究——内容全部来自调用方 data
- write 模式下擅自覆盖已存在文件（overwrite 未设 true）
- sync 模式下复制源文件内容到索引（索引只链接不重复）
- sync 模式下自动修改 README（README 是人读叙述文档，不在机械对账范围）

**ALWAYS：**
- write 模式按模板骨架忠实填入 data，遵守模板内附的纪律说明
- sync 模式按调用方 scope 更新，不做无谓全量扫描
- 两者都返回写入/更新的文件路径列表
