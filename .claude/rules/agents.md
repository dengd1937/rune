# Agent 编排

## 可用 Agent

| Agent | 用途 |
|-------|------|
| planner | 实现方案规划 |
| tdd-guide | [已废弃] 由 task-driven-development skill 内部 general-purpose + implementer-prompt.md 替代 |
| code-reviewer | [已废弃] 由 task-driven-development skill 内部 general-purpose + code-quality-reviewer-prompt.md 替代 |
| security-reviewer | 安全分析（auth/输入/支付相关强制） |
| refactor-cleaner | 清理死代码 |
| docs-lookup | Context7 查文档 |
| python-reviewer | Python 代码审查 |
| typescript-reviewer | TypeScript/React 代码审查 |
| e2e-runner | [已废弃] 由 task-driven-development skill 内部 implementer subagent 替代 |
| design-reviewer | 设计产物审查 |
| doc-writer | 工作流产出的格式化写入（模板+路径） |
| doc-updater | 跨工作流共享知识维护（catalog、索引、codemap） |
| architect | 应用架构分析（技术选型、模块边界、数据模型） |

## 关键 Skill

| Skill | 用途 | 触发方式 |
|-------|------|---------|
| investigate | 根因分析 | bug 修复前 |
| ideate | 产品想法细化 | `/ideate` |
| design-review | 方案对抗性审查 | planner 之后、实现前 |
| retro | 任务后复盘 | 功能/修复完成后 |
| architect | 架构评估与决策记录 | `/architect` 手动触发 |
| task-driven-development | 逐任务编排（implementer subagent + 并发审查 + 修复闭环） | 标准开发流程（默认） |

## 文档 Agent 分工

- **doc-writer**：工作流产物的格式化写入（知道模板和路径）
- **doc-updater**：跨工作流共享知识的维护（知道文档拓扑和 catalog）
- 工作流完成后：先 doc-writer 写文件，再 doc-updater 更新 catalog

## 执行原则

- **独立操作并行执行**，有依赖的才串行
- **复杂问题可用分角色子 agent**（事实审查、工程、安全、一致性、冗余检查）
