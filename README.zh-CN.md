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

## 工作原理

四层防线，各司其职：

```
第一层  铁律 + 路由              using-rune skill（始终加载）
第二层  按需指导                Skills（≥1% 相关时调用）
第三层  审查强制                code-review / design-review skills 内置 prompt 模板（审查时）
第四层  物理拦截                8 个 hooks（写/提交时阻断）
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
| **Brainstorm** | `/rune:brainstorm` | 产品发现、竞品调研、功能分析、技术设计、spec delta 输出 — chore 类改动走 Scale Gate 简化路径 | `docs/changes/<feature>/`（proposal + spec delta；chore 跳过） |
| **Design** | 新 UI 功能自动路由 L1/L2 | 意图 → wireframe → 高保真 → 审查门控 | `docs/designs/` |
| **Development** | 实现阶段 | 调研 → 规划 → 逐任务 TDD → 质量门控 → 审查 → commit → finishing（apply spec delta、归档 change） | 已提交代码（80%+ 覆盖率） |

任何改动都从 `/rune:brainstorm` 入口进入——纯后端跳过 Design；chore 类改动（typo、hook 调整、文档编辑）走 Scale Gate 简化路径：edit → quality-gate → reviewer → commit，不写 spec/plan。

## 文档模型

Rune 是 spec-driven，但**不依赖外部引擎**——spec 是行为契约的事实真相，其余文档都挂在它之上。以下是 Rune 在项目 `docs/` 中搭建并维护的结构：

```
docs/
├── specs/<capability>-spec.md     # 行为契约 — WHAT，耐久真相
├── changes/<feature>/             # 活跃工作单元：proposal + spec delta + design + tasks
│   └── archive/<feature>/         # 完成后留作演化日志（proposal + delta）
├── designs/<feature>/             # UI 设计产物
├── architecture/adr/              # 跨切面决策 — WHY，耐久
├── CODEMAP.md                     # 代码结构 + 模块 → capability spec 映射
└── FEATURE-CATALOG.md             # feature 台账 + UI 组件 + 决策
```

spec 不会被随手直接改——一次改动携带自己的 delta，在收尾时落定：

```
brainstorm      →  changes/<feature>/{proposal.md, specs.md}    # OpenSpec 风格 +/− delta
writing-plans   →  changes/<feature>/{design.md, tasks.md}
finishing       →  apply specs.md delta 到 specs/  →  归档 proposal + delta  →  删 design/tasks
```

- **specs/** 按 **capability** 组织、不按 feature——一个 feature 可能触及多个 capability spec。
- **changes/** 是两空间暂存地；delta 格式（`+` ADD / `-` DROP）借鉴 OpenSpec。
- **architecture/adr/** 存跨切面决策（*为什么*）；feature 级技术设计放在 `changes/<feature>/design.md`，实现后即删。
- **`pre-spec-drift-check.sh`** 在某 specced 模块的代码改动却没更新对应 spec/delta 时告警——给手工 apply 步骤补一个机械兜底。

## Skills

| Skill | 用途 |
|-------|------|
| [using-rune](skills/using-rune/SKILL.md) | 铁律 + skill 路由 — SessionStart 自动加载 |
| [brainstorm](skills/brainstorm/SKILL.md) | 产品发现 → capability spec(s)（chore 类走 Scale Gate 简化路径） |
| [design-workflow](skills/design-workflow/SKILL.md) | UI 设计 — L1 轻量 / L2 完整 wireframe → 高保真 → 审查 |
| [pencil-design](skills/pencil-design/SKILL.md) | Pencil MCP 设计 + 代码生成 |
| [writing-plans](skills/writing-plans/SKILL.md) | 技术设计 + 任务拆解 → docs/changes/<feature>/（design.md + tasks.md）— No Placeholders、双重质量检查 |
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
| [feedback](skills/feedback/SKILL.md) | 把 rune 使用痛点整理成 GitHub issue — 对话驱动，逐条确认后提交 |
| [resolve](skills/resolve/SKILL.md) | 把已有 GitHub issue 驱动到实现并 merge、自动关闭 — 核实/决策/委托/PR Closes |
| [writing-skills](skills/writing-skills/SKILL.md) | 创建和维护 Rune skills |
| [doc-sync](skills/doc-sync/SKILL.md) | 实现后文档对账 — 更新 spec、catalog、design artifact 状态 |
| [onboard](skills/onboard/SKILL.md) | 为已有项目搭建 Rune 文档拓扑 — 生成 codemap（含模块索引）、feature catalog 和接入 ADR |
| [doc-ops](skills/doc-ops/SKILL.md) | 文档机械操作 — 按模板写产物（spec/ADR/design）或对账 FEATURE-CATALOG + CODEMAP |
| [design-review](skills/design-review/SKILL.md) | 对抗式设计产物审查 — design-workflow V2-4 hard gate，移交开发前 |

## Hooks

| Hook | 时机 | 拦截内容 |
|------|------|----------|
| `session-start` | SessionStart | 通过 using-rune skill 注入铁律 |
| `pre-bash-guard.sh` | PreToolUse | 拦截危险 shell 命令 |
| `pre-write-secrets.sh` | PreToolUse | 拦截含 API keys / secrets 的写入 |
| `pre-commit-review-check.py` | PreToolUse | 强制审查通过后才允许 git commit |
| `pre-strip-llm-attribution.sh` | PreToolUse | 拦截 `gh pr create` 中的 LLM 署名 |
| `pre-spec-drift-check.sh` | PreToolUse | spec 漂移警告（advisory）—动了 specced 模块代码却没更新 spec/delta |
| `post-write-debug.sh` | PostToolUse | 检测残留 debug 语句 |
| `post-write-quality.sh` | PostToolUse | 对超大文件和反模式发出警告 |

## 目录结构

```
rune/
├── .claude-plugin/        # Plugin manifest + marketplace 入口
├── hooks/                 # 物理拦截层
├── skills/                # 自动发现的 skills
├── CLAUDE.md              # 项目指令
├── README.md              # 英文文档
├── README.zh-CN.md        # 中文文档（本文件）
└── LICENSE                # MIT
```

## License

[MIT](LICENSE)
