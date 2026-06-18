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

### Step 1: Capability Spec 对账（apply delta + verify）

spec 是权威行为契约，代码 conform 它。本步把 change 的行为 delta **apply** 到 `docs/specs/`，并 fresh-eyes 校验。

**前置判断：定位行为 delta**

- 读 `docs/changes/<feature>/specs.md`（brainstorm / bug-fix Case B 写的 delta）
- 无 specs.md（Case A bug-fix、refactor、或无行为变更）→ 跳过 apply，仅做 verify

**Apply（specs.md 存在时）：**

把 delta 落到对应 `docs/specs/<capability>-spec.md`：
- `+` 行（ADD / MODIFY）→ 并入 spec 的 Requirements / Scenarios
- `-` 行（REMOVE）→ 从 spec 删出
- new capability（delta 全 `+`）→ 创建新 capability spec 文件
- 按 capability 分段逐段 apply

**按 context：**

| context | 动作 |
|---|---|
| `new-feature` | apply `changes/<feature>/specs.md` delta → specs/ |
| `bug-fix` **Case A**（spec 对）| 无 delta；spec **不动**，仅验代码 conform |
| `bug-fix` **Case B**（spec 错 / 缺 / 歧义）| apply `changes/<feature>/specs.md` delta → specs/（delta 在 bug-fix 流程中写）+ 代码已修 |
| `abandoned` | 跳过（Step 2 标 Abandoned）|
| refactor | 无 delta；spec **必须不动**——若发现需改 spec = 该"refactor"偷改了行为，升级或上报 |

**Fresh-eyes verify（apply 后，独立视角，非 apply 者 self-check）：**

1. **Apply 完整性**：delta 每个 `+` 是否进了 spec、每个 `-` 是否已删、MODIFY 是否替换到位
2. **code↔spec 一致**：`git diff <base_SHA>..HEAD` 的实际行为符合 apply 后的 spec 契约；代码偏离正确契约 = 实现 bug（Case A），标记不改 spec
3. **refactor 守卫**：refactor 场景 spec 有任何改动冲动 → 停，上报"疑似行为变更"

**核心**：spec 正文只在"契约本身变了"时改（经 delta apply），不为"代码变了"就抄。deviation-append 机制已废除。

### Step 2: 索引推进（FEATURE-CATALOG + CODEMAP）

调用 doc-ops skill（sync 模式，scope 同时覆盖 FEATURE-CATALOG 与 CODEMAP）：

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

- 不重写 spec 全文，也不追加 deviation record——契约变更经 `changes/<feature>/specs.md` delta apply 到具体 Requirements/Scenarios
- 不引入新的 delta spec 文档格式
- 不自动删除任何文件
- 不自动更新 README
- **不自行 commit** —— 产出留在工作树，由调用方（finishing Step 2c）统一提交
