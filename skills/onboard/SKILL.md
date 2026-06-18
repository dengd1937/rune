---
name: onboard
description: "Use when adopting Rune for an existing project — scaffolds docs/ topology, generates codemap (incl. module index), creates feature catalog (incl. component/decision sections) with Pre-Rune entries, writes adoption ADR. One-time setup for brownfield projects."
---

# Brownfield Onboard

为已有项目接入 Rune 文档拓扑。一次性脚手架，生成 Rune 工作流期望的目录结构和机械文档。不反推 spec，不创造虚假历史。

**启动时公告：** "使用 onboard skill 为本项目搭建 Rune 文档拓扑。"

## 核心原则

1. **不伪造历史** — 已有功能的 spec 就是代码本身，标记为 Pre-Rune
2. **只做脚手架** — 创建结构 + 机械文档，不做需要领域知识的分析
3. **一次运行** — 跑完后不再需要，后续由 doc-updater 维护

---

## Step 1: 项目扫描

自动检测，不问用户。

**检测项：**

- 语言：从源码文件后缀推断（`.py` / `.ts` / `.go` / `.rs` / `.java` 等）
- 框架：从配置文件推断（`package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` 等）
- 主要源码目录：`find . -maxdepth 2 -type d`（排除 node_modules、.git、__pycache__）
- 已有文档：README、ARCHITECTURE.md、docs/ 目录、wiki 等

**向用户展示扫描结果摘要**（语言、框架、源码结构、已有文档列表）。

---

## Step 2: 确认模块边界

基于 Step 1 目录扫描推断模块划分。归组规则：

- `src/` 下直接子目录 → 每个是一个模块
- Python 包（含 `__init__.py` 的目录）→ 每个是一个模块
- Go 包（含 `.go` 文件的目录）→ 每个是一个模块
- 单一源码目录无子目录 → 整个项目一个模块

**向用户展示推断结果，请求确认或调整。不跳过。**

---

## Step 3: 评估已有文档

先盘点用户现有的文档结构，**不移动任何已有文件**：

- README.md → 保留根目录，CODEMAP 中引用
- 已有架构文档 → 保留原位，CODEMAP 中引用，告知用户可手动移入 `docs/architecture/`
- 外部 wiki → 不迁移，CODEMAP 中列出链接
- 已有 `docs/` → 列出现有子目录、与 Rune 期望子目录（specs / designs / architecture/adr / changes）对比，标记缺失项

向用户报告评估结果与待补缺失子目录列表。

---

## Step 4: 创建缺失目录

基于 Step 3 评估结果，仅创建缺失的 Rune 子目录：

```bash
mkdir -p docs/specs docs/designs docs/architecture/adr docs/changes docs/changes/archive
```

`mkdir -p` 对已存在的目录是 no-op，但 Step 3 评估结果必须作为前置——避免在用户已有自定义 `docs/` 结构（如 `docs/api/`、`docs/guides/`）时无差别注入空目录而无告知。

`docs/changes/` 存活跃工作单元（`<feature>/`）；`docs/changes/archive/` 存完成后归档（proposal.md + specs.md）。

---

## Step 5: 生成 CODEMAP

按 doc-updater agent 的 codemap 格式（`docs/CODEMAP.md`）生成。从源码结构机械提取：

- 目录结构（find 结果）
- 关键模块表（Step 2 确认的模块：模块 | 职责 | 入口文件 | 主要依赖 | Capability Spec；Pre-Rune 填 `[待补充]`）
- 入口文件（从框架约定推断）
- 外部依赖（从 `package.json` / `requirements.txt` / `go.mod` 解析）
- 数据流（从框架类型推断通用模式）

无法机械推断的字段填 `[待补充]`，不猜测。

---

## Step 6: 写入 ADR 0001

调用 doc-writer agent（模板：`adr`）写入：

- 标题：Adopt Rune for Development Workflow
- 上下文：已有项目决定采用 Rune
- 决策：建立文档拓扑，已有功能标记 Pre-Rune，新功能走完整 Rune 流程
- 备选：A) 反推所有 spec（否决：高成本低价值）B) 不引入 Rune（否决：新功能无法走工作流）

此 ADR 在 Step 7 注册进 FEATURE-CATALOG 的 Decisions 段。

---

## Step 7: 创建 FEATURE-CATALOG

按 doc-updater agent 的格式创建 `docs/FEATURE-CATALOG.md`，含三段：

### Features 段

询问用户列出主要已有功能（3-10 个），以 Pre-Rune 状态写入：

```markdown
| feature-name | Pre-Rune | — | — | Done |
```

字段语义（Pre-Rune 行所有字段都由 "Pre-Rune" 隐含，按 schema 占位）：

- **Status: Pre-Rune** — 表示未走过 brainstorm/design 流程的存量功能
- **Spec：—** — 该 feature 的行为尚无 capability spec（Pre-Rune = 未 specced 的 capability；后续被 feature/bug 触及时由 brainstorm 补建 `docs/specs/<capability>-spec.md`）
- **Design Status：—** — 定义性空值（Pre-Rune 必无 design 流程产物）
- **Implementation Status: Done** — 定义性已实现（Pre-Rune 意味着代码已在仓库）

不要试图给 Pre-Rune 行填其他值。用户可跳过（直接回车），Features 段留空。

### Components 段

非 UI 项目省略本段。UI 项目留空表头，后续由 design-workflow 填充。

### Decisions 段

预填 Step 6 写入的 ADR-0001：

```markdown
| 0001 | Adopt Rune for Development Workflow | 已批准 | YYYY-MM-DD | — |
```

---

## Step 8: 验证 + 报告

1. 验证 Step 4-7 产生的所有文件存在（`docs/specs/`、`docs/designs/`、`docs/architecture/adr/`、`docs/changes/` 及 CODEMAP / FEATURE-CATALOG / ADR-0001）
2. 调用 doc-updater agent 做 README 同步评估（参考 `agents/doc-updater.md` 的「项目 README 评估」职责）—— agent 仅返回建议清单，不直接修改 README
3. 向用户展示：创建的文件树 + README 同步建议清单 + 后续步骤

不自动修改 README —— 与本 skill「不做什么」中「不修改项目根目录的 README.md」一致，由用户决定是否采纳 doc-updater 的建议。

---

## 不做什么

- 不反推已有功能的 capability spec —— `specs/` 按 capability 组织（`<capability>-spec.md`），随 feature/bug 触及时由 brainstorm 逐步补建，不在 onboard 批量生成
- 不迁移外部 wiki 内容（只引用链接）
- 不移动或修改已有文档文件
- 不修改项目根目录的 README.md
- 不为存量功能反推 Components 段（UI 项目由 design-workflow 在新设计时填充）

## Red Flags

**NEVER：**
- 反推已有功能的 spec
- 移动或修改已有文档
- 不经用户确认确定模块划分
- 在 CODEMAP 中猜测无法机械推断的信息
- 跳过 ADR 0001

**ALWAYS：**
- Step 2 用户确认模块划分
- Step 7 询问已有 feature（允许跳过）
- 无法确定的信息填 `[待补充]`
