---
name: writing-skills
description: Use when creating new skills or editing existing skills for the Meridian skill library — guides skill authoring with CSO optimization, TDD testing methodology, and anti-rationalization patterns
---

# Writing Skills

为 Meridian skill 库创建和维护 skill 的元技能。

**核心方法论：** TDD applied to process documentation — 未观察到 agent 在无 skill 时失败，就不知道 skill 是否教了正确的东西。

**启动时公告：** "使用 writing-skills skill 创建/修改 skill。"

---

## 何时创建 Skill

**创建：** agent 自然行为会出错的技术方法 | 跨项目可复用 | 模式适用广泛

**不创建：** 一次性方案 | 标准实践已有完整文档 | 项目特定约定（放 CLAUDE.md）| 可用 hook 强制执行的约束（用 hook，不浪费文档）

## 目录结构

```
.claude/skills/
  skill-name/
    SKILL.md              # 主文件（必须）
    supporting-file.*     # 仅在需要时（重参考 100+ 行、prompt 模板）
```

扁平命名空间。所有 skill 在同一可搜索空间下。

---

## CSO（Claude Search Optimization）

Description 是 Claude 决定是否加载 skill 的唯一入口。写错 = skill 形同虚设。

### Description 铁律

1. 以 "Use when" 开头，只描述**触发条件**
2. **绝不**总结 skill 的流程或内容
3. 包含具体症状、场景、上下文关键词
4. 第三人称，<500 字符

```yaml
# ❌ 总结了流程 — Claude 会按 description 执行，跳过正文
description: Use when executing plans — dispatches subagent per task with two-stage review

# ✅ 只有触发条件
description: Use when executing implementation plans with independent tasks
```

**为什么关键：** 测试证明，description 总结流程时 Claude 直接按描述执行（如只做一次审查），忽略 SKILL.md 中的详细流程图（如两段审查）。去掉流程摘要后 Claude 才会正确读取完整内容。

### 关键词覆盖

用 Claude 会搜索的词汇：错误信息（"race condition"）、症状（"flaky"）、同义词（"timeout/hang/freeze"）、工具名（实际命令、库名）。

### 命名

动词优先：`writing-skills` 非 `skill-creation`，`using-git-worktrees` 非 `git-worktree-usage`。

---

## SKILL.md 结构

### Frontmatter

```yaml
---
name: skill-name-with-hyphens  # 仅字母、数字、连字符
description: Use when [触发条件]
---
```

可选字段：`origin`（来源标记）、`metadata`（author、version 等）。

### Body

```markdown
# Skill Name

## 概述
核心原则，1-2 句。

## 何时使用
触发条件 + 不适用场景

## 核心模式
Before/after 代码对比（内联或链接到单独文件）

## 快速参考
表格或列表

## 常见错误
出错 + 修复

## Red Flags（纪律型 skill 必须）
借口 → 现实对照表
```

---

## Token 效率

using-meridian 始终加载，每个 token 都有成本。

| Skill 类型 | 目标字数 |
|-----------|---------|
| 始终加载（using-meridian） | <300 词 |
| 其他 skill | <500 词 |

**技巧：** 重参考移到单独文件，SKILL.md 只链接 | 交叉引用用 skill name 不重复内容 | 一个优质示例胜过多语言重复 | 消除与交叉引用 skill 的冗余

---

## TDD for Skills

**铁律：** NO SKILL WITHOUT A FAILING TEST FIRST

| TDD 概念 | Skill 创建对应 |
|----------|---------------|
| 测试用例 | subagent 压力场景 |
| 生产代码 | SKILL.md |
| RED | 无 skill → agent 违反规则（baseline） |
| GREEN | 有 skill → agent 遵守 |
| REFACTOR | 堵住新发现的绕过方式 |

### RED：Baseline

**无** skill 时用 subagent 运行压力场景，记录 agent 的选择、理由（逐字）、触发违反的压力类型。

### GREEN：写最小 Skill

针对 baseline 发现的具体理由写 skill。用**有** skill 的同样场景再测，确认 agent 遵守。

### REFACTOR：堵漏洞

agent 找到新理由绕过 → 加显式对策 → 重测直到无法绕过。

### 按类型测试

| Skill 类型 | 测试方法 | 成功标准 |
|-----------|---------|---------|
| 流程型（纪律执行） | 学术问题 + 压力场景 + 组合压力 | 最大压力下仍遵守 |
| 模式型（思维框架） | 识别场景 + 应用场景 + 反例 | 正确识别何时用/何时不用 |
| 参考型（文档/API） | 检索 + 应用 + 缺口测试 | 找到并正确应用信息 |

---

## Anti-Rationalization 模式

纪律型 skill 需要显式堵住绕过理由。

### 1. 显式堵住每种变体

```markdown
# ❌ 只写规则
写代码前没写测试？删掉它。

# ✅ 堵住所有变体
写代码前没写测试？删掉它。从头来。

**无例外：**
- 不保留作"参考"
- 不在写测试时"适配"已有代码
- 不看它
- 删就是删
```

### 2. 声明"字面即精神"

```markdown
**违反字面就是违反精神。**
```

切断"我在遵循精神"类借口。

### 3. Rationalization Table

从 baseline 测试收集所有借口：

```markdown
| 借口 | 现实 |
|------|------|
| "这个简单，不用测试" | 简单代码也出错。测试只要 30 秒。 |
| "先实现再补测试" | 测试立刻通过什么也证明不了。 |
```

### 4. Red Flags 列表

```markdown
## Red Flags
- 先写代码再写测试
- "这个太简单不需要"
- "这次特殊因为..."

**出现任何一条 = 停下，从头来。**
```

---

## 部署检查清单

每个 skill 创建/修改后必须完成：

- [ ] name 只含字母、数字、连字符
- [ ] description 以 "Use when" 开头，只含触发条件，第三人称，<500 字符
- [ ] 关键词覆盖（错误信息、症状、工具名）
- [ ] 清晰概述 + 核心原则
- [ ] 针对 baseline 失败的具体对策
- [ ] 一个优质代码示例
- [ ] Red Flags 列表（纪律型 skill）
- [ ] 常见错误段落
- [ ] Baseline 测试通过（无 skill → agent 违反）
- [ ] GREEN 测试通过（有 skill → agent 遵守）
- [ ] Commit 到 git

---

## Red Flags

| 借口 | 现实 |
|------|------|
| "skill 内容很清楚，不用测" | 对你清楚 ≠ 对其他 agent 清楚 |
| "只是参考文档" | 参考文档也有缺口。测检索。 |
| "测 skill 太费事" | 部署有问题的 skill 费更多事 |
| "我先写完再一起测" | 批量创建不测试 = 部署未测代码 |
| "这个改动很小不用测" | 小改动也能引入歧义 |
