---
name: design-review-codex
description: Delegate plan review to Codex via codex:codex-rescue for independent cross-model adversarial analysis. Claude Code only.
origin: meridian
---

# Design Review — Codex

通过 `codex:codex-rescue` 将方案审查委托给 Codex，获取独立的跨模型对抗性分析。

**仅适用于 Claude Code 环境。** 跨工具通用版本见 [design-review](../design-review/SKILL.md)。

## When to Activate

- 需要独立于 Claude 的第二意见时
- 方案涉及高风险决策（架构重构、新技术引入、安全相关）
- 用户希望跨模型交叉验证

可与 `design-review` 配合使用：先用 `design-review` 做 Claude 侧审查，再用本 skill 获取 Codex 独立意见，对比两者发现。

---

## 前置条件

1. Codex 插件已启用（`codex@openai-codex` in settings）
2. Review Packet 已构建完整（格式见 [design-review](../design-review/SKILL.md) 的 Review Packet 章节）

---

## 执行流程

### Step 1 — 构建 Review Packet

按 `design-review` 中定义的格式构建完整的 Review Packet。如果已在 `design-review` 中构建过，直接复用。

### Step 2 — 构建 Codex 委托 Prompt

将以下内容作为任务描述传递给 `codex:codex-rescue`：

```
你是一个独立的方案审查者。你的任务是对以下实施方案进行对抗性审查。

## 审查立场

- 默认怀疑：假设方案会以微妙、高成本的方式失败，直到证据表明相反
- 不为意图加分：不认可"后续可以优化"或"先这样再说"
- 必须有据：每个发现必须引用方案中的具体决策点
- 以攻击者、混沌工程师、边界条件探测器的视角审视

## 审查维度（每维度评分 0-10）

1. 架构合理性 — 职责划分、耦合度、扩展性、可逆性、是否过度设计
2. 实现可行性 — 技术选型验证、依赖风险、边界条件、数据一致性
3. 测试策略 — 关键路径可测性、集成测试方案、边界条件覆盖
4. 性能风险 — N+1、内存、缓存、并发瓶颈、外部调用
5. Scope Challenge — 是否超出需求、有无更简单替代方案

## 输出要求

1. 各维度评分表（维度 / 评分 / 关键发现）
2. 详细发现列表（严重级别 / 置信度 1-10 / 方案引用 / 问题 / 建议）
3. 失败模式清单（决策点 / 失败模式 / 触发条件 / 影响 / 缓解建议）
4. 结论：needs-attention 或 approve
5. 置信度 < 5 的发现降级到附录

## Review Packet

[在此处粘贴完整的 Review Packet]
```

### Step 3 — 调用 codex:codex-rescue

使用 `codex:codex-rescue` agent 执行委托：

```
调用方式：Agent tool
  subagent_type: codex:codex-rescue
  prompt: [Step 2 构建的完整 prompt]
```

**关键约束：**
- 只读审查，不允许 Codex 修改任何文件
- 输出原文不截断 — Codex 的完整响应全部呈现给用户
- 超时：5 分钟

### Step 4 — 呈现结果

将 Codex 的审查结果原文输出给用户。如果同时运行了 `design-review`（Claude 侧），进行交叉对比：

```
## 跨模型对比

### 共识发现（高置信度）
[两个模型都指出的问题 — 优先处理]

### Claude 独有发现
[仅 Claude 发现的问题]

### Codex 独有发现
[仅 Codex 发现的问题]

### 分歧点
[两个模型结论不同的地方 — 需要用户判断]
```

---

## 单独使用 vs 配合使用

| 模式 | 执行方式 | 适用场景 |
|------|----------|----------|
| 单独使用 | 只运行本 skill | 快速获取独立外部意见 |
| 配合使用 | 先 `design-review` 再本 skill | 需要深度跨模型交叉验证的高风险方案 |

配合使用时，建议先完成 Claude 侧审查，再调用 Codex，最后做交叉对比。这样 Codex 的审查完全独立于 Claude 的判断。

---

## Pass Criteria

- [ ] Review Packet 已构建完整
- [ ] Codex 委托 prompt 包含完整的审查框架和 Review Packet
- [ ] Codex 返回了完整的审查结果
- [ ] 结果已原文呈现给用户
- [ ] 如配合使用，跨模型对比已完成
