---
name: doc-sync
description: "Use during finishing phase to sync documentation with implementation — updates specs, catalogs, and design artifact status. Invoked by finishing-a-development-branch Step 2b."
---

# Doc Reconciliation

代码落地后的文档对账。比较实现结果与文档现状，更新偏离部分。

**启动时公告：** "使用 doc-sync skill 进行文档对账。"

## 输入

由调用方（finishing / brainstorm Abandoned）传入：

- **feature**：feature 名称（kebab-case）
- **base_SHA**：实现前的 HEAD（abandoned 上下文可空）
- **changed_files**：本次变更的文件列表（abandoned 上下文可空）
- **context**：`new-feature` / `bug-fix` / `abandoned`

## Context 路由

不同 context 走不同 Step 组合，避免在无意义的 Step 上空转：

| context | Step 1 Capability Spec 对账 | Step 2 索引（FEATURE-CATALOG + CODEMAP） | Step 3 Design |
|---------|------------------|------------------------------------------|---------------|
| `new-feature` | 执行（spec 不存在则跳过） | CODEMAP 重扫；FEATURE-CATALOG Status=Implemented + Impl=Done | 存在则 → Implemented |
| `bug-fix` | 执行（spec 不存在则跳过） | CODEMAP 重扫；不改 feature status | 跳过 |
| `abandoned` | 跳过 | FEATURE-CATALOG Status=Abandoned（CODEMAP 不变） | 存在则 → Abandoned |

## 执行步骤

### Step 1: Capability Spec 对账

spec 是权威行为契约，代码 conform 它。**不追加 deviation record**——契约变了就原地改正文到新契约，契约没变就不动。

**前置判断：定位受影响的 capability spec**

- 优先用 brainstorm 的 capability mapping（`docs/FEATURE-CATALOG.md` 该 feature 的 Spec 列）
- 无 mapping 时：从 `changed_files` → 模块（CODEMAP）→ 该模块的 capability spec 反推
- 无 capability spec 可定位 → 跳过本步（Pre-Rune 未 specced 的 capability，或 Truly Simple 误升级兜底）

**按 context 对账每个受影响 capability spec（`docs/specs/<capability>-spec.md`）：**

| context | spec 动作 |
|---|---|
| `new-feature` | brainstorm 已把 spec 写/改到**新契约**。校验代码 conform 新契约；代码偏离新契约 = 实现 bug，标记给调用方（**不改 spec**——契约是 brainstorm 定的意图）|
| `bug-fix` **Case A**（spec 对，代码错）| 校验代码 conform；**spec 不动** |
| `bug-fix` **Case B**（spec 错 / 缺 / 歧义）| **原地改 spec** 到正确契约（增/改/删 Requirements、Scenarios）+ 代码已修 |
| `abandoned` | 跳过（Step 2 标 Abandoned）|
| refactor | spec **必须不动**；若发现需改 spec = 该"refactor"偷改了行为，升级为 feature 或上报 |

**对账方法（每个受影响 spec）：**

1. 读 capability spec 的 Requirements / Scenarios
2. `git diff <base_SHA>..HEAD` 看实际行为变更
3. 判断实现行为是否符合 spec 契约：
   - 符合 → 不动 spec
   - 契约需变（new-feature 新行为 / Case B 契约错）→ **原地改 spec 正文**到新/正确契约
   - 代码偏离正确契约（Case A）→ 不动 spec，标记代码 bug
4. refactor 场景：spec 有任何改动冲动 → 停，上报"疑似行为变更"

**核心**：spec 正文只在"契约本身变了"时改（brainstorm 决策 / Case B），不为"代码变了"就抄。deviation-append 机制已废除。

### Step 2: 索引推进（FEATURE-CATALOG + CODEMAP）

调用 doc-updater agent，scope 同时覆盖 FEATURE-CATALOG 与 CODEMAP：

- **CODEMAP**（`new-feature` / `bug-fix`，即代码有变更时）：重扫 changed_files 的目录与模块结构，更新「目录结构」与「关键模块」表
- **FEATURE-CATALOG**，按 context：
  - `new-feature` → 该 feature 的 Status=Implemented **且** Implementation Status=Done（同时设两列，修复原仅设子列的不对称）
  - `bug-fix` → 不改 feature status（仅 CODEMAP 反映修复）
  - `abandoned` → 该 feature 的 Status=Abandoned

### Step 3: Design Artifact 状态

1. 检查 `docs/designs/<feature>/` 是否存在；不存在 → 跳过本步
2. 确定追加目标文件（按存在性 fallback）：

   | 优先级 | 文件 | 出现场景 |
   |--------|------|---------|
   | 1 | `docs/designs/<feature>/review-verdict.md` | design-workflow V2 完整路径产物 |
   | 2 | `docs/designs/<feature>/intent.md` | design-workflow L1 轻量路径产物（无 review-verdict.md） |

   两个都不存在 → 跳过本步并向调用方报告。

3. `context=new-feature` → 在目标文件末尾追加：

```markdown
## Implementation Status

**状态**：Implemented
**日期**：YYYY-MM-DD
```

4. `context=abandoned` → 在目标文件末尾追加：

```markdown
## Implementation Status

**状态**：Abandoned
**日期**：YYYY-MM-DD
**原因**：[由 finishing 传入]
```

## 不做什么

- 不重写 spec 全文，也不追加 deviation record——契约变了对具体 Requirements/Scenarios 原地改
- 不引入新的 delta spec 文档格式
- 不自动删除任何文件
- 不自动更新 README
- **不自行 commit** —— 产出留在工作树，由调用方（finishing Step 2c）统一提交
