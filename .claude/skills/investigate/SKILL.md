---
name: investigate
description: Root-cause investigation → TDD fix → code review for bugs. Complete bug fix workflow — no code changes until root cause is confirmed, then RED→GREEN→IMPROVE→review.
origin: meridian
---

# Investigate

完整的 bug 修复流程：根因调查 → TDD 修复 → 代码审查。

**启动时公告：** "使用 investigate skill 进行根因调查和修复。"

**核心原则：** 没有调查就没有修复权。根因确认报告输出之前，禁止修改任何代码。

---

## When to Activate

- 遇到 bug 或非预期行为
- 测试意外失败，原因不明
- 生产环境出现异常
- 功能表现与预期不符
- 用户明确要求调查某个问题

---

## Phase 1 — 症状描述

用自己的语言精确描述问题：

**允许读取：** 错误信息、stack trace、测试输出——这些是事实，不是猜测。
**禁止读取：** 业务代码、实现代码。

```
预期行为：[用户/系统预期发生什么]
实际行为：[实际发生了什么]
复现步骤：[最短可复现路径]
复现稳定性：[必现 / 偶现(概率) / 特定条件下]
影响范围：[哪些功能/用户/环境受影响]
首次出现：[已知最早出现时间或版本]
```

**门禁**：无法稳定复现的问题，先找到复现条件再继续。

---

## Phase 2 — 假设清单（禁止修改代码）

不看业务代码，仅凭对系统的理解，列出 3–5 个可能的根因假设：

```
假设 1：[描述] — 可能性：高/中/低
假设 2：[描述] — 可能性：高/中/低
假设 3：[描述] — 可能性：高/中/低
...
```

按可能性从高到低排序。优先验证最可能的假设，不要同时验证多个。

---

## Phase 3 — 验证与模式对比（只读，不改）

### 调查范式选择

| 范式 | 适用场景 | 主路径 |
|---|---|---|
| **Hypothesis-driven**（默认） | 业务逻辑 bug、中等深度问题、有清晰假设可静态验证 | 3a 逐一验证 |
| **Trace-driven**（条件切换） | 栈深 ≥5 层 / 触发源不明 / 数据污染类（"为什么这个值会出现在这里"） | 3d backward tracing |

两种范式可以串联：先 hypothesis-driven，发现假设无法静态收敛 → 切到 trace-driven 用运行时证据定位触发源。

### 3a. 逐一验证（hypothesis-driven 主路径）

对每个假设，找对应证据来证实或排除：

**证据来源（按优先级）：**
1. 错误日志 / 异常堆栈
2. 失败的测试输出
3. 相关代码路径（只读）
4. git log / git blame（问题引入时间）
5. 配置文件 / 环境变量
6. 外部依赖版本变更

**验证记录格式：**
```
假设 1 验证：
  证据：[找到了什么]
  结论：[证实 / 排除]
  原因：[为什么]
```

用排除法收敛，直到只剩一个假设未被排除。

### 3b. 模式对比（条件触发）

当假设收敛后，在代码库中找同类工作的代码，对比差异：

- 找到功能相似但正常工作的代码
- 逐项对比差异（不假设"这不重要"）
- 用发现更新假设清单

### 3c. 多组件系统诊断

**触发条件（满足任一即必走）：**

- 系统涉及 ≥2 个组件边界（API → Service → DB，CI → Build → Deploy，Frontend → Worker → Storage 等）
- 错误层与触发层之间隔 ≥3 个调用层级
- hypothesis 排除法收敛失败（剩 ≥2 个假设无法靠静态阅读区分）

**铁律：触发后必须先加 instrumentation 跑一次再分析，禁止跳过直接猜。**

**操作步骤：**

1. 在每个组件边界加诊断输出（log 入站数据 + log 出站数据 + 验证环境/配置传递）
2. 跑一次，收集证据
3. 分析证据 → 定位"断裂层"（哪一层入站正常但出站异常）
4. 回到 3a，针对断裂层形成新假设

**模板示例（多层 shell 链路）：**

```bash
# Layer 1: Workflow / 入口层
echo "=== Layer 1: workflow env ==="
echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

# Layer 2: 构建脚本
echo "=== Layer 2: build script env ==="
env | grep IDENTITY || echo "IDENTITY not propagated"

# Layer 3: 业务操作前的状态
echo "=== Layer 3: pre-operation state ==="
security list-keychains

# Layer 4: 操作本身
codesign --sign "$IDENTITY" --verbose=4 "$APP"
```

**模板示例（应用层调用链）：**

```typescript
// 在关心的组件边界添加临时 instrumentation（修复后必须移除）
async function gitInit(directory: string) {
  console.error('[DEBUG] gitInit entry:', {
    directory,
    cwd: process.cwd(),
    stack: new Error().stack,
  });
  await execFileAsync('git', ['init'], { cwd: directory });
}
```

**产物：** "断裂层"报告（哪一层入站 OK / 出站异常），作为 3a 新一轮假设的输入。

**清理：** 诊断 instrumentation 是临时代码，根因确认后必须从代码中移除（不允许残留进 commit；`code-quality-gate` 会扫描 `console.log` / `debugger` 等残留）。

### 3d. Backward Tracing（trace-driven 主路径）

**触发条件：**

- 错误深在调用栈底部（≥5 层）
- "为什么这个值会出现在这里"类问题（数据污染、错误目录、错误参数）
- hypothesis 列表无法静态收敛（缺少触发源信息）

**操作步骤：**

1. **观察症状**：错误信息 + 直接错误位置
2. **找直接原因**：什么代码直接导致这个错误
3. **追问：是谁调用的它？**（一层一层向上）
4. **追到原始触发点**：bad value 第一次出现的位置
5. **在源头修复，不在症状处修复**

**示例：**

```text
症状：git init 在 packages/core 创建了 .git
直接原因：execFileAsync('git', ['init'], { cwd: projectDir })
↑ 谁调用？WorktreeManager.createSessionWorktree(projectDir='')
↑ 谁传的空字符串？Session.create(name, context.tempDir)
↑ tempDir 为什么是空？setupCoreTest() 在 beforeEach 之前被访问

原始触发点：top-level 变量初始化访问了未初始化的 getter
修复：把 tempDir 改成 getter，未初始化时抛错
```

**工具：**

- `new Error().stack` 注入：在可疑函数前打印调用栈
- `console.error` 注入：测试场景下用，不用 logger（可能被吞）
- 二分定位：当某测试触发污染但不知是哪个时，用 bisection script 一个一个跑
- git blame：当怀疑是近期改动引入时

**追溯不下去时的回退：** 加 instrumentation（见 3c），让运行时证据告诉你"是谁"。

---

## Phase 4 — 根因确认报告

调查完成后，输出以下报告（在对话中，不写入文件）：

```
## 调查报告

**根因**：[一句话描述真正的问题所在]

**代码位置**：[文件路径:行号]

**触发条件**：[什么情况下会触发]

**为什么之前没被发现**：[测试盲区 / 边界条件 / 近期变更引入]

**影响范围**：[受影响的功能/模块/用户]

**排除的假设**：
- 假设 X：[排除原因]
- 假设 Y：[排除原因]

**修复方向**：[修复思路 + 需改动的文件]
```

**此时才允许修改代码。**

---

## Phase 5 — TDD 修复

### 5a. RED：写复现测试

- 最小复现，精确捕获 bug 症状
- 参考 `tdd-workflow` skill 的 RED 阶段要求
- 确认测试失败（RED 验证）

### 5b. GREEN：修根因

- 单次改动，只修根因
- 禁止 "顺手" 改别的
- 禁止 bundled refactoring
- 确认测试通过（GREEN 验证）

### 5c. IMPROVE：重构（如需要）

- 仅当有明确重构必要时执行
- 测试保持 GREEN

### 5d. 质量门控

调用 `/code-quality-gate`：格式化 → lint → 类型检查 → 调试产物检测。

**通过** → 评估 5f 触发条件 → 触发则走 5f 后回 5d / 未触发直接 Phase 6。
**失败** → 修复 → 重跑 5d。

### 5e. 3 次失败熔断

如果修复尝试 ≥3 次仍未解决（GREEN 失败或质量门控反复失败）：

**STOP。** 输出架构质疑报告：

```
## 架构质疑报告

**问题**：[原始 bug]
**尝试**：[3+ 次修复的摘要]
**模式**：
  - [ ] 每次修复暴露新的耦合/共享状态
  - [ ] 修复需要"大规模重构"才能实施
  - [ ] 每次修复在其他地方产生新症状

**建议**：[重构架构 vs. 继续修症状]
```

**与用户讨论后再决定下一步。** 不允许第 4 次盲目修复。

### 5f. 防御加固（条件触发，推荐）

**触发条件（满足任一即推荐走）：**

- 数据穿越 ≥2 层组件（与 3c 触发条件一致）
- 之前已经在某层失败过（说明单点校验不足）
- 涉及数据完整性 / 安全 / 生产事故根因
- bug 类型：输入污染 / 状态泄漏 / 错误传播

**核心理念：** "修了 bug" ≠ "bug 不会复发"。在数据流的每一层加防御，让 bug 在结构上不可能再次出现。

**与"外科手术式修改"原则的边界：**

| 范畴 | 是否属于本次修复范围 |
|---|---|
| 同一 bug 数据流上多层加校验 | ✅ 属于（不算 bundled refactoring） |
| 同一 bug 引发的关联防御（mock 绕过、跨平台边界） | ✅ 属于 |
| 顺手修复其他无关 bug | ❌ 不属于（外科手术原则适用） |
| 借机重构无关代码 | ❌ 不属于 |

**四层防御模板：**

1. **L1 — 入口校验**：在 API/模块边界拒绝明显非法输入

   ```typescript
   function createProject(name: string, workingDir: string) {
     if (!workingDir?.trim()) throw new Error('workingDir cannot be empty');
     if (!existsSync(workingDir)) throw new Error(`workingDir not found: ${workingDir}`);
   }
   ```

2. **L2 — 业务逻辑校验**：在业务操作前验证数据对本操作有意义

   ```typescript
   function initializeWorkspace(projectDir: string) {
     if (!projectDir) throw new Error('projectDir required for workspace initialization');
   }
   ```

3. **L3 — 环境守卫**：在特定上下文中拒绝危险操作

   ```typescript
   async function gitInit(directory: string) {
     if (process.env.NODE_ENV === 'test' && !directory.startsWith(tmpdir())) {
       throw new Error(`Refusing git init outside tmpdir in tests: ${directory}`);
     }
   }
   ```

4. **L4 — debug 仪表**（永久保留）：在危险操作前记录上下文供 forensics

   ```typescript
   logger.debug('About to git init', {
     directory,
     cwd: process.cwd(),
     stack: new Error().stack,
   });
   ```

**实施要求：**

- 每层校验都要有独立测试（RED → GREEN）
- 测试要验证"绕过 L1 时 L2 能拦住"——不同层互相独立
- 不是所有 bug 都需要四层；按数据流实际穿越层数决定
- L4 用 logger 不用 `console.log`，避免被 `code-quality-gate` 当作残留产物清除

**完成判定：** 每层校验都有测试覆盖，所有测试 GREEN，回到 5d 重跑质量门控。

→ 全部 GREEN → 继续 Phase 6。

---

## Phase 6 — 代码审查

质量门控通过后，调用 `/code-review` (per-task)：

- `task_text` = Phase 4 调查报告（根因 + 触发条件 + 修复方向）
- `diff` = `git diff <base_SHA>..<head_SHA>`
- 无 implementer_report（主会话直接修复，无 subagent 报告）

**APPROVE** → `/finishing-a-development-branch`
**BLOCK** → `/review-handling` → 修复 → `/code-quality-gate` → 重新 `/code-review`

---

## Red Flags

出现以下念头 = 流程偏离信号，立即停下回到完整流程。

| 借口 | 现实 |
|------|------|
| "这个简单，直接改不用调查" | 简单事最容易踩未检验假设 |
| "我先看看代码再决定" | 看代码 = 已在脑补方案；Phase 1-2 不看业务代码 |
| "第一个可疑点就是根因" | 症状 ≠ 根因；继续排除其他假设 |
| "跳过复现直接改" | 无法复现 = 无法验证修复有效性 |
| "边改边验证" | 修改代码破坏现场，无法准确判断根因 |
| "压力下跳过调查" | 系统调查比乱猜快 |
| "已经手动测过了" | 手动测试无记录、不可重放、不算覆盖率 |
| "一次改多个问题" | 无法隔离哪个改动修复了哪个问题 |
| "3+ 次了再试一次" | 3 次失败 = 可能是架构问题，不是代码问题 |
| "顺手把那个也改了" | 外科手术式修改：发现无关问题告知用户，不擅自动 |
| "多组件 bug，凭感觉猜哪层断了" | 多组件场景必须先加 instrumentation 跑一次再分析（Phase 3c 铁律） |
| "深栈 bug，在症状处修复就行" | 症状处只是错误显现点；trace 到原始触发点修复（Phase 3d） |

---

## Pass Criteria

全部完成的判断标准：

- [ ] 问题可以稳定复现
- [ ] 根因已定位到具体代码位置
- [ ] 触发条件已明确
- [ ] 调查报告已输出
- [ ] 复现测试通过 RED 验证
- [ ] 修复后测试通过 GREEN 验证
- [ ] 质量门控通过
- [ ] 代码审查 APPROVE
