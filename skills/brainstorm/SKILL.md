---
name: brainstorm
description: "You MUST use this before any creative work — creating features, building components, adding functionality, modifying behavior, or solving ambiguous problems. Guides from vague idea through product discovery, competitive research, feature analysis, technical design, and spec writing, producing a unified feature spec. Terminal state: invokes writing-plans skill (non-UI) or design-workflow skill (UI tasks). This applies to EVERY project regardless of perceived simplicity."
origin: rune
---

# Brainstorm

将模糊的产品想法精炼为包含产品定义和技术设计的统一 feature spec，输出可直接对接 Design Workflow 和 Development Workflow 的文档。

**Announce at start:** "I'm using the brainstorm skill to explore this idea and produce a feature spec."

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until either (a) Phase 5 spec is written and user has approved it, or (b) the **Scale Gate** (see below) has publicly classified the change as Truly Simple and the user has acknowledged. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A config change, a single-function utility — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

---

## Scale Gate（在 HARD-GATE 之后立即判定）

启动 brainstorm 时**第一动作**就是对改动规模做公开判定。匹配 **Truly Simple** 时走简化路径，绕过 Phase 2/3/4/5/6 但保留质量门与审查闸。

### Truly Simple 判定（必须全部满足）

- 单文件改动，且实际变更 ≤30 行
- 无新文件、无新依赖、无新模块、无新数据模型
- 无新行为：不改业务逻辑、不改 API 契约、不改公开接口
- 典型场景：修 typo / 改注释 / 调 hook regex / 调 README / 配置项调整 / skill 措辞调整

任一不满足 → 走完整 6-Phase 流程。

### Truly Simple 路径（chore-light）

1. **公开判定**：在第一条消息中显式公告 "Scale Gate 判定为 Truly Simple：[一句话说明改什么]"
2. **用户确认**：等用户明确认可（"go"/"ok"/"对"/"动手"等即可）
3. **跳过** Phase 2/3/4/5/6 —— 不写 spec 文件、不进入 writing-plans、不进入 subagent-driven-development
4. **执行链**：edit → `/code-quality-gate` → `/code-review` (per-task 模式，code-quality-reviewer-prompt) → commit（Conventional Commits）

### 仍不可绕过

- post-edit `/code-quality-gate`（format/lint/typecheck/debug 扫描）
- `/code-review` per-task（hook `pre-commit-review-check.py` 物理强制）
- commit 走 Conventional Commits（hook `pre-bash-guard.sh` 物理强制）
- 涉及 secrets / 认证 / DB 查询 / 文件系统 / 加密 → 仍触发安全审查（code-quality-reviewer-prompt.md 内置 OWASP Top 10）

### 用户随时可驳回

用户回应 "走完整 brainstorm" 或 "这不算 chore" → 立即放弃 Truly Simple 判定，回到 Phase 1。

### 反逃避

- **NEVER** 自判 Truly Simple 直接 edit 而不公告判定
- **NEVER** 把"≤30 行"作为唯一标准（行数小但改业务逻辑 = 不是 chore）
- **NEVER** 把 reviewer/quality-gate 也跳过（这是 L3，不可绕）
- **NEVER** 把多个 chore 攒一块跑（每个 chore 走自己的简化链）

### Abandoned 判定

用户明确表示"不做了"/"取消"/"放弃"时：

1. **公告**：在消息中显式说明 "Feature [name] 标记为 Abandoned"
2. **检查已有产物**：`docs/specs/<feature>-design.md` 或 `docs/designs/<feature>/` 是否已存在
3. **已有产物** → 调用 `/doc-sync`（`context=abandoned`）标记状态
4. **无产物** → 仅更新 catalog（如已在 Phase 5 写入了 spec，走 3；如仍在 Phase 1-4，无产物需处理）
5. **用户确认**

不走完整的 Scale Gate 或 Phase 流程。

---

## 核心原则

> PM 的职责是追问和挑战，不是附和。

- 不急着给出答案，先确保问题被正确理解
- 主动识别用户未说出的假设
- 每一步都有明确的完成标准，信息不够不进入下一步
- 输出的文档是下游工作流的输入，格式必须精确对接

---

## Phase Overview

```
Phase 1: Product Discovery（必经）
    │
    ├─▶ Phase 2: Competitive Research（可选）
    │
    ├─▶ Phase 3: Feature Analysis
    │
    ├─▶ Phase 4: Technical Design（纯 UI 可跳过）
    │
    ├─▶ Phase 5: Spec Writing（Phase 4 完成时必经）
    │
    └─▶ Phase 6: Routing
```

---

## Phase 1 — Product Discovery（必经入口）

通过自由式对话，帮用户从一个模糊想法梳理出产品轮廓。

**执行方式：**

根据用户的 idea 类型，动态选择追问方向。不使用固定问题模板，而是根据对话内容即时追问。

**追问维度参考（按需选用，不全问）：**

```
问题空间：
- 这个产品解决什么痛点？现在用户怎么解决？
- 目标用户是谁？有没有具体的用户画像？
- 使用场景是什么？什么时候、在什么情况下会用？

产品形态：
- 是 Web / App / 小程序 / 平台 / 工具？
- 用户第一次打开会看到什么？
- 核心使用流程是怎样的？（1-2 分钟 walk-through）

价值与边界：
- 做成什么样的算成功？什么样的算失败？
- 有什么是明确不做的？
- 跟现有工具/方案相比，独特之处是什么？
```

**追问节奏：**

- 每轮对话最多问 2-3 个问题，不要一次抛出所有问题
- 根据用户的回答追问更深，而不是换话题
- 当用户开始重复已说过的内容时，说明信息已经足够

**输出（不写文件，在对话中确认）：**

```
## 产品轮廓

**一句话描述**：[产品是什么，给谁，解决什么问题]

**目标用户**：[用户画像]

**产品形态**：[Web / App / 平台 / 工具]

**核心场景**：
1. [场景描述]
2. [场景描述]

**初版功能清单**：
- [功能 1]：[简要描述]
- [功能 2]：[简要描述]
- ...

**明确的边界（不做什么）**：
- ...
```

**完成门槛：** 用户确认产品轮廓准确，无重大遗漏。

**然后主动提议：** 「产品轮廓已明确，是否进入竞品调研？也可以直接跳到功能分析或技术设计。」

---

## Phase 2 — Competitive Research（可选）

通过 web search 找到已有解决方案，列出功能对比。

**执行方式：**

1. 根据产品轮廓提取搜索关键词
2. 使用 WebSearch / Context7 搜索竞品和替代方案
3. 整理为功能对比表

**搜索策略：**

```
第一轮搜索：[产品类型] + "tools" / "platform" / "app" / "alternatives"
第二轮搜索：针对发现的具体竞品，搜索功能评测和用户评价
```

**输出（不写文件，在对话中确认）：**

```
## 竞品分析

**竞品列表**：

| 竞品 | 定位 | 核心功能 | 定价模式 | 备注 |
|------|------|----------|----------|------|
| [竞品 1] | ... | ... | 免费/付费/SaaS | ... |
| [竞品 2] | ... | ... | ... | ... |

**功能对比**：

| 功能 | 本产品 | 竞品 1 | 竞品 2 | 竞品 3 |
|------|--------|--------|--------|--------|
| [功能 1] | ✓ | ✓ | ✗ | ✓ |
| [功能 2] | ✓(差异化) | ✗ | ✓ | ✗ |
| ... | ... | ... | ... | ... |

**市场空白**：
- [发现的未被满足的需求或功能缺口]

**对我们的启发**：
- [竞品做得好的地方可以参考]
- [竞品做得不好的地方是我们的机会]
```

**如果没有找到直接竞品：**

说明这是一个相对空白的市场，分析间接替代方案（用户当前用什么方式解决这个问题）。

**完成门槛：**
- 找到竞品时：用户确认竞品列表合理，无遗漏的主要竞品
- 未找到竞品时：用户确认间接替代方案合理，空白市场判断成立

**然后主动提议：** 「竞品分析已完成，是否进入功能分析？」

---

## Phase 3 — Feature Analysis

将功能清单进行优先级排序，定义 MVP 范围。

**执行方式：**

1. 回顾 Phase 1 的功能清单 + Phase 2 的竞品启发
2. 与用户讨论每个功能的优先级
3. 确定哪些是 MVP 必须有的，哪些可以后续迭代

**优先级标准：**

```
P0 — MVP 必须：没有这个功能，产品不成立
P1 — 重要但可延后：有了更好，没有也能用
P2 — 锦上添花：时间允许再做

判定依据：
- 这个功能去掉后，核心场景还能跑通吗？→ 不能 = P0
- 竞品都有这个功能吗？且用户会因此流失吗？→ 是 = P1
- 这个功能是"有了更好"还是"必须有"？→ 前者 = P2
```

**输出（不写文件，在对话中确认）：**

```
## 功能分析

**MVP 定义**：
MVP 范围 = P0 功能集合，目标是 [一句话描述 MVP 交付的核心价值]

**功能优先级**：

| 功能 | 优先级 | 理由 | 依赖 |
|------|--------|------|------|
| [功能 1] | P0 | [为什么必须] | 无 |
| [功能 2] | P0 | [为什么必须] | [功能 1] |
| [功能 3] | P1 | [为什么重要] | 无 |
| [功能 4] | P2 | [为什么锦上添花] | [功能 3] |

**功能依赖关系**：
[功能 A] → [功能 B]（B 依赖 A 先完成）

**迭代规划建议**：
- V1 (MVP)：P0 功能
- V2：P1 功能
- V3：P2 功能
```

**完成门槛：** 用户确认 MVP 范围合理，优先级无争议。

**然后主动提议：** 「功能分析已完成，是否进入技术设计？」

---

## Phase 4 — Technical Design

将产品定义转化为技术方案。根据复杂度走 L1 或 L2 路径。

### L1 / L2 路由

| 条件 | 级别 | 深度 |
|------|------|------|
| 单模块内改动，技术栈不变，无新依赖 | L1（轻量） | 简要方案对比 + 核心设计决策 |
| 跨模块、新依赖、数据模型变更、系统集成 | L2（标准） | 完整方案比选 + 详细设计 |

### 4a. Codebase Context Gathering

在提出技术方案前，先了解现状：

- 读取现有 ADR（`docs/architecture/adr/*.md`），了解已有决策和约束
- 读取 codemap（`docs/CODEMAP.md`），了解项目整体结构
- 读取相关模块文档（`docs/modules/*.md`），了解模块职责和公共 API
- 读取相关产品文档，了解需求上下文
- 扫描相关源码，了解当前实现

### 4b. Propose 2-3 Technical Approaches

提出至少 2 个技术方案，每个方案包含：

```markdown
## 方案 A：[名称]

**描述**：[方案描述]

**优点**：
- [...]

**缺点**：
- [...]

**影响范围**：[...]

**实现复杂度**：低/中/高

---

## 方案 B：[名称]

[同上格式]
```

给出推荐方案和理由。

### 4c. Present Design in Sections

对推荐方案（或用户选择的方案），分段展示设计。每段确认后再进入下一段。

**Scale each section to its complexity**：简单的几句话即可，复杂的可到 200-300 字。

**覆盖维度：**

1. **Architecture** — 整体架构、组件划分、模块交互
2. **Components** — 核心组件职责和接口
3. **Data Flow** — 数据流向、状态管理、持久化策略
4. **Error Handling** — 错误分类、恢复策略、边界情况
5. **Testing** — 测试策略、关键测试场景

### 4d. Analysis Dimensions Checklist

每个方案评估时，按以下维度检查（作为 review checklist，不单独产出）：

**Technical Selection（技术选型）：**
- 与现有技术栈的兼容性
- 社区活跃度和维护状态
- 学习曲线和团队熟悉度
- 长期维护成本（升级、安全补丁）
- 许可证合规性

**Module Boundaries（模块边界）：**
- 单一职责原则
- 模块间依赖方向（避免循环依赖）
- 公共 API 最小化
- 高内聚低耦合

**Data Model（数据模型）：**
- 实体关系和规范化程度
- 扩展性（未来需求）
- 查询模式和性能
- 迁移策略和数据完整性

**API Contract（API 契约）：**
- RESTful 设计原则
- 版本策略
- 错误模式一致性
- 认证和授权策略

**System Integration（系统集成）：**
- 边界划分（谁负责什么）
- 通信方式（同步/异步）
- 数据同步策略
- 故障隔离和容错

### 4e. User Confirms Approach Selection

展示推荐方案和理由，**等待用户明确选择**。不自行推进。

用户可以选择推荐方案、其他方案，或要求混合/修改。

**完成门槛：** 用户明确选择了技术方案。

---

## Phase 5 — Spec

将 Phase 1-4 的所有决策写入统一的 feature spec。

### 5a. Write Spec

调 doc-writer agent 写入 spec：

→ doc-writer agent 模板：`feature-spec`
  feature: `<feature-name>`
  data: Phase 1 产品轮廓 + Phase 2 竞品分析 + Phase 3 功能分析 + Phase 4 技术设计 + 路由决策

doc-writer 将格式化并写入 `docs/specs/<feature>-design.md`。

**Spec 文件必须包含以下 metadata block（文件头部）：**

```markdown
---
feature: <canonical-feature-name>
spec: docs/specs/<canonical-feature-name>-design.md
routing: [Design Workflow L2 | Development Workflow | L1 Lightweight Design]
---
```

`feature` 字段是下游所有 skill 的寻址锚点——design-workflow 用它定位 `docs/designs/<feature>/`，writing-plans 用它定位 `docs/plans/<feature>.md`。命名必须在 Phase 5 首次写入时确定，后续不再更改。

**写入后：**
→ doc-updater agent 更新 feature catalog

### 5b. Spec Self-Review

写完 spec 文件后，用 fresh eyes 做四项检查：

1. **Placeholder scan** — 搜索 TBD、TODO、不完整章节、模糊需求。发现问题立即修复。
2. **Internal consistency** — 各章节是否矛盾？架构描述是否与功能描述一致？
3. **Scope check** — 是否聚焦到单个实现计划？覆盖多个独立子系统则需拆分。
4. **Ambiguity check** — 是否存在两种解读的需求？如有，选一种并显式说明。

发现问题 inline 修复，不需要 re-review 循环。

### 5c. User File-Level Review Gate

Self-review 通过后，**请用户审阅 spec 文件**：

> "Spec written to `docs/specs/<feature>-design.md`. Please review it and let me know if you want to make any changes before we proceed to implementation planning."

等待用户确认。如果用户要求修改，修改后重新执行 5b self-review。只有用户批准后才进入 Phase 6。

---

## Phase 6 — Routing

根据功能性质判断后续工作流路径：

```
判断依据：
1. 是否涉及 UI？
   - 否 → 纯 Development Workflow
   - 是 → 继续

2. UI 复杂度如何？
   - 小改动（按钮、文案、布局微调）→ L1 轻量设计 → Development Workflow
   - 新页面/新组件/新交互 → L2 标准设计流程 (V2-1 到 V2-4) + Development Workflow
```

**输出（在对话中确认）：**

```
## 路由决策

后续工作流：[Design Workflow L2 / Development Workflow / L1 Lightweight Design]
理由：[一句话]
```

路由决策是建议而非强制，用户可以否决并调整路径。

---

## Phase 间跳转规则

| 从 | 可跳到 | 条件 |
|----|--------|------|
| Phase 1 | Phase 3 | 跳过竞品直接排优先级 |
| Phase 1 | Phase 4 | 用户已有清晰产品定义，不需要竞品和优先级 |
| Phase 2 | Phase 4 | 跳过优先级直接进入技术设计 |
| Phase 4 | Phase 3 | 技术设计中发现需要重新评估功能范围 |
| 任意 Phase | Phase 6 | 用户说"够清楚了，直接开干" |

**不可跳过：**
- Phase 1（必须理解问题）
- Phase 5（如果 Phase 4 已完成，必须写 spec）

---

## Pass Criteria

- [ ] 产品轮廓经过用户确认
- [ ] 竞品列表和功能对比经过用户确认（如执行了 Phase 2）
- [ ] MVP 范围和优先级经过用户确认
- [ ] 技术方案经过用户确认（如执行了 Phase 4）
- [ ] Spec 文件已写入并通过 self-review
- [ ] 用户已审阅 spec 文件并批准
- [ ] 路由决策经过用户确认
- [ ] doc-writer 已写入 spec 文件
- [ ] 用户明确表示「可以进入下一步」

---

## Common Mistakes

**错误：附和用户而不是追问**
- 用户说"我需要一个 X 功能"时，不急着记录，先问"为什么需要？解决什么问题？"
- 避免"好主意！"式的肯定，用"这个想法有意思，能多说说…"来引导深入

**错误：把用户要求当作用户需求**
- 用户说"加个搜索"可能是"信息太多了找不到"的问题，搜索不一定是唯一解
- 区分 wants（用户说的）和 needs（用户真正需要的）

**错误：过早收敛到具体方案**
- Phase 1 的目标是理解问题空间，不是设计解决方案
- 如果用户一开始就描述具体功能，引导回"这个功能解决什么问题"

**错误：跳过竞品调研直接定义功能**
- 即使是创新产品，了解已有方案能避免重复造轮子
- 竞品的不足是最有价值的产品方向信号

**错误：MVP 范围过大**
- MVP 应该是"最小可验证"，不是"最小可用产品"
- 如果 MVP 需要超过 5 个 P0 功能，可能还不够聚焦

**错误：跳过 spec self-review**
- 写完 spec 后必须过一遍 placeholder/consistency/scope/ambiguity 四项检查
- "写完了直接给用户看" 等于跳过了质量门控

**错误：不经用户审阅直接进入 planning**
- spec 文件必须经过用户审阅并明确批准
- "我写完了，开始做计划吧" 不算用户批准

---

## 与现有工作流的衔接

```
/brainstorm
  │
  ├─ Phase 1-4 → doc-writer agent template: feature-spec → docs/specs/<feature>-design.md
  │                                                                     │
  │              design-workflow V2-1 消费此文件
  │              writing-plans skill 消费此文件
  │
  └─ doc-updater agent 更新 feature catalog
```
