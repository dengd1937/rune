# Rune

[English](README.md)

Claude Code 工程纪律插件 — 通过铁律和 hook 物理拦截强制执行 TDD、安全审查和质量门控。

## 快速上手

```bash
# 添加 marketplace
claude plugin marketplace add dengd1937/rune

# 安装 plugin
claude plugin install rune@rune
```

安装后自动激活：

- **SessionStart** hook 在启动、clear、compact 时注入铁律
- **PreToolUse** hook 拦截危险命令和 secrets 写入
- **PostToolUse** hook 检测 debug 语句和质量问题
- **Skills** — 通过 `/rune:<skill-name>` 调用（完整列表见下方表格）
- **3 个 agents** — design-reviewer、doc-writer 等

## 工作原理

四层防线，各司其职：

```
第一层  铁律 + 路由              using-rune skill（始终加载）
第二层  按需指导                Skills（≥1% 相关时调用）
第三层  审查强制                code-review skill 内置 prompt 模板（审查时）
第四层  物理拦截                6 个 hooks（写/提交时阻断）
```

**铁律**（不可绕过）：

- **L1** — 每个任务独立运行 TDD → 实现 → 审查循环
- **L3** — 未经审查的代码无法提交（hook 硬拦截）

chore 类改动（typo、hook regex、README 调整）走 `brainstorm` skill 的 **Scale Gate** 简化路径——quality-gate、reviewer、commit hook 仍不可绕。

## 工作流

```
/rune:brainstorm ─→ /rune:design-workflow ─→ /rune:subagent-driven-development
  产品+技术设计           UI 设计                    逐任务开发
```

| 阶段 | 触发 | 做什么 | 产出 |
|------|------|--------|------|
| **Brainstorm** | `/rune:brainstorm` | 产品发现、竞品调研、功能分析、技术设计、spec 输出 — chore 类改动走 Scale Gate 简化路径 | `docs/specs/`（chore 跳过） |
| **Design** | 新 UI 功能自动路由 L1/L2 | 意图 → wireframe → 高保真 → 审查门控 | `docs/designs/` |
| **Development** | 实现阶段 | 调研 → 规划 → 逐任务 TDD → 质量门控 → 审查 → commit | 已提交代码（80%+ 覆盖率） |

任何改动都从 `/rune:brainstorm` 入口进入——纯后端跳过 Design；chore 类改动（typo、hook 调整、文档编辑）走 Scale Gate 简化路径：edit → quality-gate → reviewer → commit，不写 spec/plan。

## Skills

| Skill | 用途 |
|-------|------|
| [using-rune](skills/using-rune/SKILL.md) | 铁律 + skill 路由 — SessionStart 自动加载 |
| [brainstorm](skills/brainstorm/SKILL.md) | 产品发现 → feature spec（chore 类走 Scale Gate 简化路径） |
| [design-workflow](skills/design-workflow/SKILL.md) | UI 设计 — L1 轻量 / L2 完整 wireframe → 高保真 → 审查 |
| [pencil-design](skills/pencil-design/SKILL.md) | Pencil MCP 设计 + 代码生成 |
| [writing-plans](skills/writing-plans/SKILL.md) | 实施方案 — 任务拆解、No Placeholders、双重质量检查 |
| [subagent-driven-development](skills/subagent-driven-development/SKILL.md) | 多文件改动 — 逐任务 TDD + 审查循环 |
| [tdd-workflow](skills/tdd-workflow/SKILL.md) | RED → GREEN → IMPROVE 循环（80%+ 覆盖率） |
| [investigate](skills/investigate/SKILL.md) | 根因分析 → TDD 修复 → 审查（未确认原因前不改代码） |
| [code-quality-gate](skills/code-quality-gate/SKILL.md) | 编辑后质量门禁 — 格式、类型检查、debug 检测 |
| [code-review](skills/code-review/SKILL.md) | 审查调度 — 按语言路由到对应 reviewer |
| [commit-quality](skills/commit-quality/SKILL.md) | 提交前检查 — 格式、lint、secrets 扫描 |
| [review-handling](skills/review-handling/SKILL.md) | 处理 BLOCK 反馈 — 去重、分类、排序 |
| [verifying-before-completion](skills/verifying-before-completion/SKILL.md) | 验证门禁 — 声明成功前必须运行新鲜命令 |
| [finishing-a-development-branch](skills/finishing-a-development-branch/SKILL.md) | 实现后 — 验证测试、清理产物、呈现合并选项 |
| [using-git-worktrees](skills/using-git-worktrees/SKILL.md) | 通过 git worktree 创建隔离并行工作区 |
| [python-patterns](skills/python-patterns/SKILL.md) | Pythonic 模式、类型注解、异常处理、包组织 |
| [typescript-patterns](skills/typescript-patterns/SKILL.md) | TypeScript/React 模式、shadcn/ui、Tailwind v4 |
| [django-security](skills/django-security/SKILL.md) | Django 认证鉴权、CSRF/XSS/SQLi、生产安全配置 |
| [security-reviewer](skills/security-reviewer/SKILL.md) | 敏感功能开发与提交前的安全审查清单 |
| [retro](skills/retro/SKILL.md) | 任务复盘 — 流程遵守、决策质量、改进建议 |
| [writing-skills](skills/writing-skills/SKILL.md) | 创建和维护 Rune skills |
| [doc-sync](skills/doc-sync/SKILL.md) | 实现后文档对账 — 更新 spec、module doc、catalog、design artifact 状态 |
| [onboard](skills/onboard/SKILL.md) | 为已有项目搭建 Rune 文档拓扑 — 生成 codemap、模块索引、catalog 和接入 ADR |

## Agents

| Agent | 用途 | 触发时机 |
|-------|------|----------|
| [design-reviewer](agents/design-reviewer.md) | 设计产物审查 | 设计工作流各阶段 |
| [doc-writer](agents/doc-writer.md) | 按模板格式化并写入工作流文档 | 工作流产出结构化数据后 |
| [doc-updater](agents/doc-updater.md) | 维护 catalog、索引、codemap | 工作流完成后 |

## Hooks

| Hook | 时机 | 拦截内容 |
|------|------|----------|
| `session-start` | SessionStart | 通过 using-rune skill 注入铁律 |
| `pre-bash-guard.sh` | PreToolUse | 拦截危险 shell 命令 |
| `pre-write-secrets.sh` | PreToolUse | 拦截含 API keys / secrets 的写入 |
| `pre-commit-review-check.py` | PreToolUse | 强制审查通过后才允许 git commit |
| `post-write-debug.sh` | PostToolUse | 检测残留 debug 语句 |
| `post-write-quality.sh` | PostToolUse | 对超大文件和反模式发出警告 |

## 目录结构

```
rune/
├── .claude-plugin/        # Plugin manifest + marketplace 入口
├── hooks/                 # 物理拦截层
├── skills/                # 自动发现的 skills
├── agents/                # 3 个自动发现的 agents
├── CLAUDE.md              # 项目指令
├── README.md              # 英文文档
├── README.zh-CN.md        # 中文文档（本文件）
└── LICENSE                # MIT
```

## License

[MIT](LICENSE)
