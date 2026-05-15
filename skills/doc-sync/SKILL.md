---
name: doc-sync
description: "Use during finishing phase to sync documentation with implementation — updates specs, module docs, catalogs, and design artifact status. Invoked by finishing-a-development-branch Step 2b."
---

# Doc Reconciliation

代码落地后的文档对账。比较实现结果与文档现状，更新偏离部分。

**启动时公告：** "使用 doc-sync skill 进行文档对账。"

## 输入

由 finishing skill 传入：

- **feature**：feature 名称（kebab-case）
- **base_SHA**：实现前的 HEAD
- **changed_files**：本次变更的文件列表
- **context**：`new-feature` / `bug-fix` / `abandoned`

## 执行步骤

### Step 1: Spec 对账

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

1. 检查 `docs/designs/<feature>/` 是否存在
2. 存在且 `context=new-feature` → 在 `review-verdict.md` 末尾追加：

```markdown
## Implementation Status

**状态**：Implemented
**日期**：YYYY-MM-DD
```

3. 存在且 `context=abandoned` → 追加：

```markdown
## Implementation Status

**状态**：Abandoned
**日期**：YYYY-MM-DD
**原因**：[由 finishing 传入]
```

4. 不存在 → 跳过

## 不做什么

- 不重写 spec 全文
- 不引入新的 delta spec 文档格式
- 不自动删除任何文件
- 不自动更新 README
