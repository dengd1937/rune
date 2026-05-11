# Meridian — Claude Code Agent Baseline

## 核心原则

1. **Agent 优先** — 将领域任务委托给专用 agent
2. **测试驱动** — 先写测试再实现，80%+ 覆盖率要求
3. **安全优先** — 安全不妥协；验证所有输入
4. **不可变性** — 永远创建新对象，禁止原地修改
5. **先规划后执行** — 复杂功能编码前先规划
6. **逐任务执行** — 多文件改动按任务拆分，每个任务独立走 TDD+审查

## 规则索引

| 关注领域 | 规则文件 | 详细指导 |
|---------|---------|---------|
| Agent 与 Skill 编排 | [agents.md](rules/agents.md) | — |
| 代码质量、安全、测试 | [common.md](rules/common.md) | code-quality-gate skill / security-reviewer agent / tdd-workflow skill |
| 代码审查流程 | [code-review.md](rules/code-review.md) | code-reviewer agent |
| 交互原则 | [communication.md](rules/communication.md) | — |
| 开发工作流 | skill 链路（见 using-meridian §6） | brainstorm → writing-plans → subagent-driven-development → finishing-a-development-branch |
| Git 规范 | [git-workflow.md](rules/git-workflow.md) | git-workflow skill |
| 设计工作流（路由） | [design-workflow.md](rules/design-workflow.md) | design-workflow skill |
| 语言规范 | [languages.md](rules/languages.md) | python-patterns skill / typescript-patterns skill |

## 快速参考

- **开发流程：** 调研 → 规划 → **逐任务循环（TDD→质量门控→审查）** → 文档 → Commit → 预审查
- **Commit 格式：** `<type>: <description>` — 类型：feat, fix, refactor, docs, test, chore, perf, ci
- **关键 Agent：** commit 前 → code-reviewer + security-reviewer；bug 修复前 → investigate

## 验收标准

- 测试覆盖率 80%+，无安全漏洞，满足用户需求

## UI 生成规则

- 项目根目录存在 `DESIGN.md` 时，在开始任何设计工作及每个主要设计阶段前必须读取。其色彩、字体、组件样式、布局原则、层级规则、行为规范和响应式行为作为硬性约束 — 不是建议。
- `DESIGN.md` 不存在时，无视觉约束地继续工作。
- `DESIGN.md` 在工作流中只读：永远不要为迁就设计而修改它，应修改设计本身。
