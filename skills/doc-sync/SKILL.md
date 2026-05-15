---
name: doc-sync
description: "Use during finishing phase to sync documentation with implementation — updates specs, module docs, catalogs, and design artifact status. Invoked by finishing-a-development-branch Step 2b."
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

| context | Step 1 Spec 对账 | Step 2 Module Doc | Step 3 Catalog | Step 4 Design |
|---------|------------------|-------------------|----------------|---------------|
| `new-feature` | 执行（spec 不存在则跳过） | 执行 | Status → Done | 存在则 → Implemented |
| `bug-fix` | 执行（spec 不存在则跳过） | 执行 | 不改 feature status | 跳过 |
| `abandoned` | 跳过 | 跳过 | Status → Abandoned | 存在则 → Abandoned |

## 执行步骤

### Step 1: Spec 对账

**前置判断（spec 不存在则跳过本步）：**

```bash
test -f docs/specs/<feature>-design.md
```

| 条件 | 行为 |
|------|------|
| spec 文件不存在 | 跳过 Step 1，直接进 Step 2 |
| spec 文件存在 | 继续以下流程 |

跳过场景：

- `context=bug-fix` 且 feature 是 Pre-Rune（onboard 标记的已有功能）
- `context=bug-fix` 且 feature 从未走过 brainstorm 完整流程
- 用户主动绕过 brainstorm 直接修改代码（Truly Simple 路径误升级到完整流程的兜底）

**spec 存在时的对账流程：**

1. 读取 spec 文件（`docs/specs/<feature>-design.md`）
2. 计算 diff：`git diff <base_SHA>..HEAD`
3. 比对 spec 的 Technical Design 各子章节（Architecture / Data Model / API Contract / Error Handling）与 diff 实际变更
4. 有偏离 → 在 spec 的 Technical Design 章节末尾追加 deviation record：

```markdown
### Implementation Deviations

#### [YYYY-MM-DD] — [feature/fix description]
**偏差章节**：Architecture
**原方案**：[spec 中的描述]
**实际实现**：[diff 中的实现]
**原因**：[为什么偏离]
```

5. 无偏离 → 不改 spec

不重写 spec，只追加偏离记录。保留原始决策上下文。

### Step 2: Module Doc 对账

**前置判断**：`context=abandoned` 或 `changed_files` 为空 → 跳过本步。

1. 从 changed_files 提取涉及的模块列表
2. 对每个模块：
   - `docs/modules/<module>.md` 存在 → 读取现有内容 → 读取源码当前公共 API → 比对 → 有差异则更新 API 表和用法示例
   - `docs/modules/<module>.md` 不存在 → 创建新 module doc（读源码提取公共 API）
3. 模块判断标准：changed_files 中的文件按目录层级归组

### Step 3: Catalog 状态推进

根据 context 参数：

- `new-feature` → FEATURE-CATALOG 中该 feature 的 Implementation Status 改为 Done
- `bug-fix` → 不改 feature status，但更新 MODULE-INDEX（Step 2 已更新 module doc）
- `abandoned` → FEATURE-CATALOG 中该 feature 的 Status 改为 Abandoned

调用 doc-updater agent 执行 catalog 更新。

### Step 4: Design Artifact 状态

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

- 不重写 spec 全文
- 不引入新的 delta spec 文档格式
- 不自动删除任何文件
- 不自动更新 README
- **不自行 commit** —— 产出留在工作树，由调用方（finishing Step 2c）统一提交
