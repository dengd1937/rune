---
name: resolve
description: "Use when you have one or more existing GitHub issues to resolve — whether collected via the feedback skill from external users or filed by a maintainer. Verifies each issue against the codebase's actual state, decides whether it is worth fixing, routes implementation to existing workflows, and closes the loop via PR with Closes #N. A thin orchestrator: it delegates design/implementation to existing skills and only owns issue verification, the worth-fixing decision, and PR/merge wiring."
origin: rune
---

# Resolve

把"已存在的 GitHub issue"驱动到"实现并 merge、issue 自动关闭"。**薄编排层**——核实与决策自己做，设计/实现全委托现有 skill。

**启动时公告：** "使用 resolve skill 处理 issue [#N...]。"

## 适用边界

- 适用：已存在一个或多个 GitHub issue（feedback 收来的，或开发者 `gh issue create` 记下的）想做掉
- **不强制**："所有改动必须先建 issue"。开发者临时小改动仍可直接走 brainstorm Scale Gate（chore-light），不必为此建 issue。本 skill 是"有 issue 时的标准路径"，不是"所有改动入口"

## 输入

- 一个或多个 issue number / URL（同一仓库）

## Phase 1 — 核实

对每个 issue：

1. `gh issue view <N>` 读取完整内容
2. **核对本体当前实际状态**——读相关代码 / skill / 配置，验证 issue 描述的行为是否真实存在。**不照 issue 描述就改**
3. 判定：
   | 结论 | 处理 |
   |------|------|
   | 真问题 | 进 Phase 2 |
   | 认知偏差 / 已修复 / 无法复现 | 在 issue 回复说明依据，关闭或请补充，**不进入实现** |

## Phase 2 — 决策

对核实成立的 issue：

1. **值不值得改**——三维评估：
   - 影响面：多大范围、多高频
   - 修复代价：改动量 / 跨文件 / 风险
   - 反作用风险：过度防御、流程负担、削弱既有约束
2. 定位根因与落点
3. 多 issue → 找共性：是否同一主线（统一设计），还是彼此独立（各自处理）
4. **不自动判定**——把"是否值得改 + 落点"呈现给用户裁决。判定不值得改 → issue 回复理由，问用户是否仍要做

## Phase 3 — 路由实现（委托，不重做）

按规模路由到现有 skill，**不复述其内容**：

| 规模 | 委托 |
|------|------|
| chore 级（单文件、≤30 行、无新行为） | brainstorm Scale Gate (Truly Simple) → 直接 edit |
| bug 且根因不明 | investigate |
| 多文件 / 新设计 / 跨模块 | brainstorm → writing-plans → subagent-driven-development |

实现产物的每个 commit 关联对应 issue（commit body 写 `Refs: <repo>#N`，最终关闭由 Phase 4 的 `Closes` 完成）。

## Phase 4 — PR 收尾

1. **委托 finishing-a-development-branch**——传入 `linked_issues`（本批 issue 编号）。finishing 负责测试验证、产物清理、并在选项 1 的 PR body 写入 `Closes #N`
2. finishing 走到"PR 已创建（含 Closes #N）"后，本 skill 接管：
   - 用户 review PR
   - 满意 → `gh pr merge --rebase --delete-branch`（保持线性历史）
   - **验证**：`gh issue list --state all` 确认本批 issue 已自动关闭
3. 若 PR 需迭代 → 留给用户，不强行 merge

## 明确不做

- 不重做 investigate 的根因分析 / SDD 的逐任务实现 / finishing 的测试与清理 / brainstorm 的设计——全部委托
- 不复述被委托 skill 的内容；Phase 3/4 只放路由表与委托钩子
- 不自动判"值得改"——决策点由用户裁决
- 不强制所有改动建 issue（见适用边界）
- 不加独立 Red Flags 堆叠——复用被委托 skill 的护栏

## Red Flags

**NEVER：**
- 照 issue 描述直接改而不核对本体当前状态
- 跳过 Phase 2 决策直接进入实现
- 自行判定"值得改"不经用户裁决
- 在 Phase 3/4 复述被委托 skill 的执行细节

**ALWAYS：**
- 每个 issue 先核对本体验证真实性
- 决策点呈现给用户
- 实现委托现有 skill，本 skill 只编排
- merge 后验证 issue 确实自动关闭
