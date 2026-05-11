# 设计工作流（路由）

> 完整流程在 `design-workflow` skill 中，按需加载。

## 激活条件

| 激活 | 跳过 |
|---|---|
| 新 UI 功能 / 页面 / 组件 / 视觉改动 | 纯后端 / 配置 / 文档修改 |
| 新 token / 新交互模型 | 无视觉变化的重构 |
| 涉及 `docs/designs/`、`.pen`、Pencil MCP | 不涉及 UI |

## L1 vs L2 路由

- **L1（轻量）**：无新 token、无新组件、无新页面、无新交互 → 加载 `design-workflow` skill L1
- **L2（标准）**：其他所有 UI 工作 → 加载 `design-workflow` skill V2-1 到 V2-5

L2 Gate 3 通过后的产物（intent.md、screenshots/、components/、tokens/）进入 `writing-plans` → `subagent-driven-development` 链路。开发时通过 Pencil MCP 实时读取设计属性。

## DESIGN.md

- **存在时**：作为视觉身份唯一权威（SSOT），设计工作流（L1 和 L2）从中派生 token 并以其为设计护栏
- **不存在时**：现有流程不变
- **默认只读**：工作流不会静默回写 DESIGN.md；设计需求超出范围时先记录 design identity gap，默认收敛设计，只有用户明确确认视觉身份变更时才更新 DESIGN.md
- **预检**：DESIGN.md 存在时先检查 9 模块完整性；缺失信息作为 gap 处理，不由模型臆造默认审美

## 文档维护

设计工作流（L1 或 L2）完成后：
→ doc-updater agent 更新 component catalog 和 feature catalog
