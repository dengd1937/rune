# Meridian — Claude Code Agent Baseline

## 目录结构

```text
meridian/
├── .claude-plugin/
│   └── marketplace.json               # Marketplace catalog
├── plugins/
│   └── meridian/                      # Plugin directory（分发包）
│       ├── .claude-plugin/
│       │   └── plugin.json            # Plugin manifest
│       ├── skills/                    # 26 skills
│       ├── agents/                    # 11 agents
│       └── hooks/
│           ├── hooks.json             # Hook configuration（CLAUDE_PLUGIN_ROOT）
│           ├── session-start          # 铁律注入
│           └── ...
├── .claude/                           # 开发环境（settings.json hooks，CLAUDE_PROJECT_DIR）
│   ├── skills/                        # 26 skills（开发用副本）
│   ├── agents/                        # 11 agents（开发用副本）
│   ├── hooks/                         # Hook 脚本（开发用副本）
│   ├── settings.json
│   └── settings.local.json
├── CLAUDE.md
├── README.md
└── docs/
```

## 双源维护

`.claude/`（开发）和 `plugins/meridian/`（分发）中的 skills/agents/hooks 是两份独立副本。唯一的差异在 `session-start` hook：
- `.claude/hooks/session-start` 使用 `CLAUDE_PROJECT_DIR`
- `plugins/meridian/hooks/session-start` 使用 `CLAUDE_PLUGIN_ROOT`

修改任一侧的 skill/agent/hook 后，必须手动同步到另一侧。

## 使用方式

### Plugin Marketplace（推荐）

```bash
claude plugin marketplace add sdeng079/meridian
claude plugin install meridian@meridian
```

### 开发环境

本 repo 的 `.claude/` 目录用于开发。`settings.json` 中的 hooks 使用 `CLAUDE_PROJECT_DIR` 引用 `.claude/hooks/` 下的脚本。修改 skills/agents/hooks 后需同步到 `plugins/meridian/`。

## 核心原则

1. **Agent 优先** — 将领域任务委托给专用 agent
2. **测试驱动** — 先写测试再实现，80%+ 覆盖率要求
3. **安全优先** — 安全不妥协；验证所有输入
4. **不可变性** — 永远创建新对象，禁止原地修改
5. **先规划后执行** — 复杂功能编码前先规划
6. **逐任务执行** — 多文件改动按任务拆分，每个任务独立走 TDD+审查

## 规范分层

| 层 | 内容 | 加载时机 |
|---|---|---|
| **铁律 + 路由 + 行为护栏** | using-meridian skill（SessionStart hook 注入） | 始终 |
| **Skill 按需指导** | 各 skill（brainstorm、git-workflow、python-patterns、typescript-patterns 等） | 调用时 |
| **Agent 审查强制** | reviewer agents（code-quality-reviewer-prompt、python-reviewer、typescript-reviewer、security-reviewer） | 审查时 |
| **Hook 物理拦截** | pre-write-secrets.sh、pre-bash-guard.sh、post-write-quality.sh、pre-commit-review-check.py | 写/提交时 |

## 验收标准

- 测试覆盖率 80%+，无安全漏洞，满足用户需求

## UI 生成规则

- 项目根目录存在 `DESIGN.md` 时，在开始任何设计工作及每个主要设计阶段前必须读取。其色彩、字体、组件样式、布局原则、层级规则、行为规范和响应式行为作为硬性约束 — 不是建议。
- `DESIGN.md` 不存在时，无视觉约束地继续工作。
- `DESIGN.md` 在工作流中只读：永远不要为迁就设计而修改它，应修改设计本身。
