---
name: retro
description: Post-task retrospective. Reflects on workflow adherence, decision quality, and AI behavior — then proposes targeted improvements to rules/skills/agents for user approval.
origin: meridian
---

# Retro

任务结束后，对本次实现过程做系统性复盘。**审视决策路径，不审视代码质量**（那是 code-reviewer 的职责）。

## When to Activate

- 一个功能或 bug 修复完成后
- 感觉本次实现走了弯路
- 发现某条规则被反复跳过
- 想评估当前工作流是否适合该类任务

用户主动调用，不强制。

---

## Retro Workflow

### Phase 1 — 任务还原

用一段话描述本次任务的**原始目标**和**实际完成内容**：

```
原始目标：[用户最初要求什么]
实际完成：[最终做了什么]
差异：[有没有多做、少做、或偏离目标]
```

---

### Phase 2 — 流程审视

对照开发工作流的 8 个步骤，逐项检查是否被遵守：

| 步骤 | 是否执行 | 备注 |
|------|----------|------|
| 1. Research & Reuse | ✓ / ✗ / 不适用 | |
| 2. Plan First | ✓ / ✗ / 不适用 | |
| 3. TDD Approach | ✓ / ✗ / 不适用 | |
| 4. Quality Gate | ✓ / ✗ / 不适用 | |
| 5. Code Review | ✓ / ✗ / 不适用 | |
| 6. Documentation Decision | ✓ / ✗ / 不适用 | |
| 7. Commit & Push | ✓ / ✗ / 不适用 | |
| 8. Pre-Review Checks | ✓ / ✗ / 不适用 | |

**重点关注**：被跳过的步骤是合理豁免，还是规则执行不到位？

---

### Phase 3 — 决策复盘

回顾本次实现过程中的关键决策节点：

```
决策 1：[做了什么选择] → [结果如何] → [有没有更好的选择]
决策 2：...
```

关注：
- 有没有走了弯路后将就收场？
- 有没有先实现后才发现更简单的方案？
- 依赖选型、架构选择是否经过充分考量？

---

### Phase 4 — AI 行为审视

诚实评估 Claude 本次的行为模式：

```
Scope Creep：有没有做了用户没要求的事？
规则违反：有没有跳过 Hard Gate 或强制步骤？
过度谨慎：有没有不必要地打断用户要求确认？
上下文丢失：有没有因为对话过长而遗忘早期上下文？
```

---

### Phase 5 — 建议改进（需用户确认才执行）

基于以上复盘，列出对 rules/skills/agents 的具体修改建议：

```
建议 1：[目标文件] [具体改动]
  理由：[为什么这次暴露了这个问题]
  优先级：高 / 中 / 低

建议 2：...
```

**输出后停下来，询问用户：「是否需要应用以上建议？」**

不主动修改任何文件。

---

## Output Format

所有内容在对话中输出，不写入文件。格式参考：

```
## Retro Report

### 任务还原
...

### 流程审视
...

### 决策复盘
...

### AI 行为审视
...

### 建议改进（需用户确认）
...
```

---

## 常见发现模式

| 现象 | 可能的根因 | 改进方向 |
|------|-----------|----------|
| 反复跳过某个步骤 | 规则描述不清晰 or 触发条件不明确 | 更新对应 rule |
| 走了弯路才发现更简单方案 | Research 阶段不够充分 | 加强 Research & Reuse 检查项 |
| 做了用户没要求的事 | 缺少 scope 边界意识 | 在 plan 阶段明确 out-of-scope |
| 同类 bug 重复出现 | investigate skill 执行不到位 | 检查 Hard Gate 是否被遵守 |
