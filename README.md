# meridian

Claude Code engineering discipline plugin — TDD, security review, quality gates enforced through iron laws and hook-based physical interception.

## 安装

```bash
# 添加 marketplace
claude plugin marketplace add sdeng079/meridian

# 安装 plugin
claude plugin install meridian@meridian
```

安装后自动激活：
- SessionStart hook 注入铁律（startup / clear / compact）
- PreToolUse hook 拦截危险命令和 secrets
- PostToolUse hook 检测 debug 语句和代码质量
- 26 个 skills（通过 `/meridian:<skill-name>` 调用）
- 11 个 agents（含 reviewer、doc-writer 等）

## 目录结构

```text
meridian/
├── .claude-plugin/
│   └── marketplace.json               # Marketplace catalog
├── plugins/
│   └── meridian/                      # Plugin directory
│       ├── .claude-plugin/
│       │   └── plugin.json            # Plugin manifest
│       ├── skills/                    # 26 skills（auto-discovered）
│       ├── agents/                    # 11 agents（auto-discovered）
│       └── hooks/
│           ├── hooks.json             # Hook configuration
│           ├── session-start          # 铁律注入（CLAUDE_PLUGIN_ROOT）
│           ├── pre-bash-guard.sh
│           ├── pre-write-secrets.sh
│           ├── post-write-debug.sh
│           ├── post-write-quality.sh
│           ├── pre-commit-review-check.py
│           └── lib/utils.sh
├── .claude/                           # Dev environment（settings.json hooks）
├── CLAUDE.md
├── README.md
└── docs/
```

## 工作流

从想法到代码，三条工作流按需串联：

```
/meridian:brainstorm ─→ /meridian:design-workflow ─→ /meridian:subagent-driven-development
  产品+技术设计            UI 设计                      逐任务开发
```

| 阶段 | 触发 | 做什么 | 产出 |
|------|------|--------|------|
| **Brainstorm** | `/meridian:brainstorm` | 产品发现、竞品调研、功能分析、技术设计、spec 输出 | `docs/specs/` |
| **Design** | 新 UI 功能自动路由 L1/L2 | 意图 → wireframe → 高保真 → 审查门控 | `docs/designs/`（tokens、组件契约） |
| **Development** | 实现阶段 | 调研 → 规划 → 逐任务 TDD → 质量门控 → 审查 → commit | 已提交代码（80%+ 覆盖率） |

三条工作流独立可用 — 纯后端功能跳过 Design，无 UI 变更的重构跳过 Brainstorm 和 Design。

## Skills

| Skill | 用途 |
|---|---|
| [brainstorm](plugins/meridian/skills/brainstorm/SKILL.md) | 产品发现+技术设计+spec 输出 — 从想法到统一 feature spec |
| [design-workflow](plugins/meridian/skills/design-workflow/SKILL.md) | UI 设计工作流 V2 — L1 轻量 / L2 标准（wireframe → 高保真 → 审查 → 交付） |
| [pencil-design](plugins/meridian/skills/pencil-design/SKILL.md) | Pencil MCP 设计与代码生成 — token 管理、组件映射、视觉验证 |
| [design-review](plugins/meridian/skills/design-review/SKILL.md) | 方案对抗性审查 — 压力测试架构、可行性、测试、性能与范围 |
| [design-review-codex](plugins/meridian/skills/design-review-codex/SKILL.md) | 通过 Codex 获取独立跨模型方案审查（Claude Code 专用） |
| [tdd-workflow](plugins/meridian/skills/tdd-workflow/SKILL.md) | 测试驱动开发，执行 RED → GREEN → IMPROVE |
| [code-quality-gate](plugins/meridian/skills/code-quality-gate/SKILL.md) | 编辑文件后的质量门禁（格式、类型检查、调试代码检测） |
| [code-review](plugins/meridian/skills/code-review/SKILL.md) | 代码审查调度 — 按语言和场景分派 reviewer，返回 APPROVE/BLOCK |
| [commit-quality](plugins/meridian/skills/commit-quality/SKILL.md) | 提交前质量检查（commit 格式、lint、secrets 扫描） |
| [git-workflow](plugins/meridian/skills/git-workflow/SKILL.md) | commit / push / PR / CI / merge 全流程闭环 |
| [python-patterns](plugins/meridian/skills/python-patterns/SKILL.md) | Pythonic 模式、类型注解、异常处理、包组织 |
| [python-testing](plugins/meridian/skills/python-testing/SKILL.md) | pytest、TDD、fixtures、mock、覆盖率与测试分层 |
| [typescript-patterns](plugins/meridian/skills/typescript-patterns/SKILL.md) | TypeScript/React 模式、shadcn/ui、Tailwind v4 |
| [typescript-testing](plugins/meridian/skills/typescript-testing/SKILL.md) | Vitest + React Testing Library + Playwright E2E |
| [django-security](plugins/meridian/skills/django-security/SKILL.md) | Django 认证鉴权、CSRF/XSS/SQL 注入、生产安全配置 |
| [security-reviewer](plugins/meridian/skills/security-reviewer/SKILL.md) | 敏感功能开发与提交前的安全审查清单、漏洞模式与防护建议 |
| [e2e-testing](plugins/meridian/skills/e2e-testing/SKILL.md) | Playwright E2E 测试模式、POM、CI 集成、flaky 测试治理 |
| [investigate](plugins/meridian/skills/investigate/SKILL.md) | 根因分析门禁 — 假设优先调试，禁止无调查改代码 |
| [retro](plugins/meridian/skills/retro/SKILL.md) | 任务复盘 — 审视流程遵守、决策路径与 AI 行为，提出改进建议 |
| [review-handling](plugins/meridian/skills/review-handling/SKILL.md) | 处理 BLOCK 审查反馈 — 去重、分类、排序、评估 pushback |
| [using-git-worktrees](plugins/meridian/skills/using-git-worktrees/SKILL.md) | Git worktree 并行开发，减少 stash 和上下文切换 |
| [finishing-a-development-branch](plugins/meridian/skills/finishing-a-development-branch/SKILL.md) | 实现完成后验证测试、清理产物、呈现集成选项 |
| [verifying-before-completion](plugins/meridian/skills/verifying-before-completion/SKILL.md) | 实现或修复后的验证门禁 — 运行新鲜命令确认成功 |
| [subagent-driven-development](plugins/meridian/skills/subagent-driven-development/SKILL.md) | 多文件改动按任务编排 — 逐任务 TDD+审查循环 |
| [writing-plans](plugins/meridian/skills/writing-plans/SKILL.md) | 实施方案规划 — 任务拆解、No Placeholders、自检+plan-reviewer 双重质量保障 |
| [writing-skills](plugins/meridian/skills/writing-skills/SKILL.md) | Skill 元技能 — CSO 优化、TDD 测试方法论、anti-rationalization 模式 |

## Agents

| Agent | 用途 | 触发时机 |
|---|---|---|
| [design-reviewer](plugins/meridian/agents/design-reviewer.md) | 设计产物审查 | 设计工作流 V2-4 |
| [doc-writer](plugins/meridian/agents/doc-writer.md) | 工作流文档写入（模板格式化+写文件） | 工作流产出文档后 |
| [doc-updater](plugins/meridian/agents/doc-updater.md) | 跨领域文档维护（catalog、索引、codemap） | 工作流完成后 |
| [docs-lookup](plugins/meridian/agents/docs-lookup.md) | 通过 Context7 查阅文档 | API / 文档查询 |
| [python-reviewer](plugins/meridian/agents/python-reviewer.md) | Python 代码审查 | Python 项目 |
| [security-reviewer](plugins/meridian/agents/security-reviewer.md) | 安全漏洞检测 | 提交前、敏感代码 |
| [refactor-cleaner](plugins/meridian/agents/refactor-cleaner.md) | 死代码清理 | 代码维护 |
| [tdd-guide](plugins/meridian/agents/tdd-guide.md) | 测试驱动开发 | 新功能、bug 修复、行为调整 |
| [typescript-reviewer](plugins/meridian/agents/typescript-reviewer.md) | TypeScript / React / Next.js 代码审查 | TypeScript / Next.js 项目 |

## 三层文档架构

工作流产出文档经过两层 agent 处理，形成闭环：

```
工作流（brainstorm / design / development）
  │  产出结构化数据（对话中确认）
  ▼
doc-writer agent（独立上下文）
  │  按模板格式化 → 写入文件
  ▼
文件落盘（docs/specs/、docs/designs/、docs/modules/）
  │
  ▼
doc-updater agent（独立上下文）
  │  更新 catalog / 索引 / codemap
  ▼
共享知识层同步
```

- **工作流**：只产出结构化数据，不写文件、不含模板
- **doc-writer**：集中管理文档模板，接收数据后格式化写入
- **doc-updater**：维护 feature catalog、component catalog、module index、codemap，评估 README 同步需求

## 开发说明

本 repo 同时包含开发环境（`.claude/`）和分发包（`plugins/meridian/`）。

- `.claude/`：开发时使用，`settings.json` hooks 使用 `CLAUDE_PROJECT_DIR`
- `plugins/meridian/`：分发包，`hooks.json` 使用 `CLAUDE_PLUGIN_ROOT`
- 修改 skills/agents/hooks 时需同步两边

## 设计原则

- Rules 已下放 — 铁律和行为护栏在 using-meridian（SessionStart hook 注入），具体规范在 skills（按需加载）和 reviewer agents（审查时强制），hooks 提供物理拦截
- 文档模板集中管理（doc-writer agent），工作流不含内联模板
- Hooks 提供确定性安全执行层（物理拦截），using-meridian 提供行为护栏

## License

MIT
