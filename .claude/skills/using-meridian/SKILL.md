---
name: using-meridian
description: Use when starting any conversation or after compact - establishes Meridian iron laws, skill invocation rules, and red flags
---

<SUBAGENT-STOP>
如果你是被派发到具体任务的 subagent，跳过此 skill。
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
你拥有 Meridian 工程基线。下列铁律不可绕过。

如果一个 skill 有 ≥1% 概率适用于当前任务，你**必须** invoke 它。

这不是建议，不是可选项，你不能合理化绕过。
</EXTREMELY-IMPORTANT>

## §1 IRON LAWS

```
╔════════════════════════════════════════════════════════════════════╗
║  L1 — 每任务独立走 TDD→实现→审查循环，禁止跨任务合并审查            ║
║  L2 — 降级必须用户明确批准，模型不得自判"简单"跳过流程              ║
║  L3 — 未通过审查的代码不许 commit（hook 硬阻塞，禁 --no-verify）    ║
╚════════════════════════════════════════════════════════════════════╝
```

违反字面就是违反精神。三条铁律不分轻重，任意一条被绕过即视为流程失败。

## §2 Skill 调用元规则

**规则**：用户消息进来 → 检查是否有 skill 适用 → 有 1% 可能 ⇒ invoke Skill 工具 → 公告"使用 [skill] 来 [目的]" → 严格按 skill 执行。

**优先级**：
1. 用户显式指令（CLAUDE.md / 直接请求）—— 最高
2. Meridian skill —— 覆盖默认行为
3. 默认系统提示 —— 最低

**关键**：skill 调用**先于**阅读代码、**先于** clarifying questions。"我先看看代码再决定" 等于已经在脑补方案，必须先 skill。

## §3 产出约束

- **不主动创建 *.md** —— 分析、总结、说明直接在对话里给。例外：`docs/plans/` 由 development-workflow 要求创建，完成后必须删
- **临时测试脚本**（`test_*.py` / `verify_*.py`）执行后**立即**删除 —— 验证完就是冗余代码
- **不可变性（CRITICAL）** —— 永远创建新对象，禁止原地修改
- **外科手术式修改** —— 发现无关问题告知用户，不擅自动手

## §4 Red Flags：跳过 skill / 流程

这些念头出现 = 流程偏离信号，立即停下回到完整流程。

| 借口 | 现实 |
|---|---|
| "这个简单，直接做不用 skill" | 简单事最容易踩未检验假设 |
| "我先看看代码再决定要不要 skill" | 看代码=已在脑补方案；skill 调用先于阅读 |
| "我记得这个 skill 怎么用" | skill 会演化，每次按当前版本读 |
| "用户没说要走流程" | 用户说 WHAT，规则定义 HOW |
| "这次只改一行，跳过 TDD" | 一行也能引入回归，30 秒写测试 |
| "几个任务一起审查更高效" | 跨任务合并审查不允许（IRON LAW 1） |

## §5 Red Flags：跳过审查 / commit

| 借口 | 现实 |
|---|---|
| "改动很小，CRITICAL 不可能存在" | 一行就能引入 SQL 注入、原型污染、TOCTOU |
| "代码看起来挺干净，应该没问题" | 没经过 reviewer agent = 没审查；自我感觉不算 |
| "reviewer 误报了，跳过吧" | 误报需说明具体理由由用户确认，不许自行驳回 |
| "我顺手把那个无关问题修了" | 外科手术式：发现无关问题告知用户，不擅自动 |
| "现在赶时间，先 commit 再说" | 没审查的代码不许 commit（IRON LAW 3，hook 阻塞） |
| "我已经手动测过了" | 手动测试无记录、不可重放、不算覆盖率 |

## §6 流程与产物指针

| 场景 | 入口 |
|---|---|
| 标准开发流程（默认） | `task-driven-development` skill |
| bug 修复（先于读代码） | `investigate` skill |
| 产品发现+技术设计+spec 输出 | `brainstorm` skill / `/brainstorm` |
| UI 任务 | `design-workflow` skill（DESIGN.md 检查由 skill 内部处理） |
| commit 前质量门 | `commit-quality` skill |
| 任务后复盘 | `retro` skill |

**常用 agent**（清单见 `.claude/agents/`）：security-reviewer / python-reviewer / typescript-reviewer

## §7 工程边界

第一次写代码就要遵守的硬约束（其余规范由对应 reviewer agent 在审查时强制）：

- **Python**：必须 `uv add <pkg>`，禁止 `pip` / `poetry` / `conda` / `uv pip install`（hook 强制）
- **TypeScript**：禁止 `any`（用 `unknown` 收窄）；禁止硬编码颜色 / 字体 / 圆角 / 阴影（必须用 token）

## §8 Hook 行为

若被 hook 阻塞，按 hook 输出**修复根因**，禁止 `--no-verify` / `--no-gpg-sign` 等绕过（IRON LAW 3）。
