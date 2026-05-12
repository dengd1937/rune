# meridian

Claude Code agent 基准线 — 沉淀可跨项目复用的 rules、skills 与 agents，让 Claude Code 开箱即用。

## 目录结构

```text
meridian/
├── CLAUDE.md                        # 项目入口：核心原则、规则索引、UI 规则
├── .claude/
│   ├── agents/                      # Agent 定义（planner、code-reviewer 等）
│   ├── hooks/                       # 安全与质量 hook 脚本
│   ├── rules/                       # （已清空 — 规范已下放到 skills/agents/using-meridian）
│   ├── skills/                      # 按需加载的详细指导
│   │   ├── brainstorm/
│   │   ├── code-quality-gate/
│   │   ├── commit-quality/
│   │   ├── design-review/
│   │   ├── design-review-codex/
│   │   ├── design-workflow/
│   │   ├── django-security/
│   │   ├── e2e-testing/
│   │   ├── git-workflow/
│   │   ├── investigate/
│   │   ├── pencil-design/
│   │   ├── python-patterns/
│   │   ├── python-testing/
│   │   ├── retro/
│   │   ├── security-reviewer/
│   │   ├── subagent-driven-development/
│   │   ├── tdd-workflow/
│   │   ├── typescript-patterns/
│   │   ├── typescript-testing/
│   │   ├── writing-skills/
│   │   └── using-git-worktrees/
│   ├── settings.json                # Hook 与权限配置
│   └── settings.local.json          # 本地 MCP 权限
└── docs/                            # 文档产物（plans、designs、modules）
```

## 工作流

从想法到代码，三条工作流按需串联：

```
/brainstorm ─→ design-workflow ─→ subagent-driven-development
  产品+技术设计     UI 设计           逐任务开发
```

| 阶段 | 触发 | 做什么 | 产出 |
|------|------|--------|------|
| **Brainstorm** | `/brainstorm` | 产品发现、竞品调研、功能分析、技术设计、spec 输出 | `docs/specs/` |
| **Design** | 新 UI 功能自动路由 L1/L2 | 意图 → wireframe → 高保真 → 审查门控 | `docs/designs/`（tokens、组件契约） |
| **Development** | 实现阶段 | 调研 → 规划 → 逐任务 TDD → 质量门控 → 审查 → commit | 已提交代码（80%+ 覆盖率） |

三条工作流独立可用 — 纯后端功能跳过 Design，无 UI 变更的重构跳过 Brainstorm 和 Design。

## Skills

| Skill | 用途 |
|---|---|
| [brainstorm](.claude/skills/brainstorm/SKILL.md) | 产品发现+技术设计+spec 输出 — 从想法到统一 feature spec |
| [design-workflow](.claude/skills/design-workflow/SKILL.md) | UI 设计工作流 V2 — L1 轻量 / L2 标准（wireframe → 高保真 → 审查 → 交付） |
| [pencil-design](.claude/skills/pencil-design/SKILL.md) | Pencil MCP 设计与代码生成 — token 管理、组件映射、视觉验证 |
| [design-review](.claude/skills/design-review/SKILL.md) | 方案对抗性审查 — 压力测试架构、可行性、测试、性能与范围 |
| [design-review-codex](.claude/skills/design-review-codex/SKILL.md) | 通过 Codex 获取独立跨模型方案审查（Claude Code 专用） |
| [tdd-workflow](.claude/skills/tdd-workflow/SKILL.md) | 测试驱动开发，执行 RED → GREEN → IMPROVE |
| [code-quality-gate](.claude/skills/code-quality-gate/SKILL.md) | 编辑文件后的质量门禁（格式、类型检查、调试代码检测） |
| [commit-quality](.claude/skills/commit-quality/SKILL.md) | 提交前质量检查（commit 格式、lint、secrets 扫描） |
| [git-workflow](.claude/skills/git-workflow/SKILL.md) | commit / push / PR / CI / merge 全流程闭环 |
| [python-patterns](.claude/skills/python-patterns/SKILL.md) | Pythonic 模式、类型注解、异常处理、包组织 |
| [python-testing](.claude/skills/python-testing/SKILL.md) | pytest、TDD、fixtures、mock、覆盖率与测试分层 |
| [typescript-patterns](.claude/skills/typescript-patterns/SKILL.md) | TypeScript/React 模式、shadcn/ui、Tailwind v4 |
| [typescript-testing](.claude/skills/typescript-testing/SKILL.md) | Vitest + React Testing Library + Playwright E2E |
| [django-security](.claude/skills/django-security/SKILL.md) | Django 认证鉴权、CSRF/XSS/SQL 注入、生产安全配置 |
| [security-reviewer](.claude/skills/security-reviewer/SKILL.md) | 敏感功能开发与提交前的安全审查清单、漏洞模式与防护建议 |
| [e2e-testing](.claude/skills/e2e-testing/SKILL.md) | Playwright E2E 测试模式、POM、CI 集成、flaky 测试治理 |
| [investigate](.claude/skills/investigate/SKILL.md) | 根因分析门禁 — 假设优先调试，禁止无调查改代码 |
| [retro](.claude/skills/retro/SKILL.md) | 任务复盘 — 审视流程遵守、决策路径与 AI 行为，提出改进建议 |
| [using-git-worktrees](.claude/skills/using-git-worktrees/SKILL.md) | Git worktree 并行开发，减少 stash 和上下文切换 |
| [subagent-driven-development](.claude/skills/subagent-driven-development/SKILL.md) | 多文件改动按任务编排 — 逐任务 TDD+审查循环 |
| [writing-plans](.claude/skills/writing-plans/SKILL.md) | 实施方案规划 — 任务拆解、No Placeholders、自检+plan-reviewer 双重质量保障 |
| [writing-skills](.claude/skills/writing-skills/SKILL.md) | Skill 元技能 — CSO 优化、TDD 测试方法论、anti-rationalization 模式、token 效率 |

## Agents

| Agent | 用途 | 触发时机 |
|---|---|---|
| `planner` | [已废弃] 由 writing-plans skill 替代 | — |
| `tdd-guide` | 测试驱动开发 | 新功能、bug 修复、行为调整 |
| `code-reviewer` | 代码质量与可维护性审查 | 编写或修改代码后 |
| `security-reviewer` | 安全漏洞检测 | 提交前、敏感代码 |
| `design-reviewer` | 设计产物审查 | 设计工作流 V2-4 |
| `refactor-cleaner` | 死代码清理 | 代码维护 |
| `doc-writer` | 工作流文档写入（模板格式化+写文件） | 工作流产出文档后 |
| `doc-updater` | 跨领域文档维护（catalog、索引、codemap） | 工作流完成后 |
| `docs-lookup` | 通过 Context7 查阅文档 | API / 文档查询 |
| `python-reviewer` | Python 代码审查 | Python 项目 |
| `typescript-reviewer` | TypeScript / React / Next.js 代码审查 | TypeScript / Next.js 项目 |
| `e2e-runner` | [已废弃] 由 implementer subagent 替代 | — |

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
- **doc-writer**：集中管理 8 个文档模板，接收数据后格式化写入
- **doc-updater**：维护 feature catalog、component catalog、module index、codemap，评估 README 同步需求

## DESIGN.md

`DESIGN.md` 是一份放在项目根目录的纯 Markdown 文件，定义项目的视觉设计系统（色彩、字体、组件样式、布局、响应式等），供 AI agent 生成 UI 时参照。源自 [Google Stitch](https://stitch.withgoogle.com/docs/design-md/overview) 提出的标准，采用 9 模块结构。

### 为什么需要它

没有 DESIGN.md 时，AI agent 生成的 UI 会趋向通用风格（圆角卡片、蓝紫渐变、居中 Hero）。引入后，agent 在生成任何 UI 前自动读取 DESIGN.md 作为视觉约束，输出与品牌风格一致的结果。

meridian 不自带具体项目审美。它只提供读取、校验和执行 DESIGN.md 的工作流；具体 DESIGN.md 应由下游项目根据产品定位、品牌资产和用户审美自行选择或编写。

### 如何获取

**方式一：从社区收藏选择起点**

[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) 收录了 55+ 品牌设计系统模板（Stripe、Linear、Vercel、Apple 等），适合作为参考或改写起点：

```bash
# 在项目根目录执行，自动下载 DESIGN.md
npx getdesign@latest add linear.app
```

也可在 [getdesign.md](https://getdesign.md) 在线浏览和预览。

> 社区模板不等于品牌授权。生产项目使用真实品牌风格前，需要确认授权、商标/品牌风险，并根据当前项目定位改写。

**方式二：从已有设计系统整理**

如果项目已有 Figma token、Tailwind config、品牌指南等，按 [DESIGN.md 9 模块结构](https://getdesign.md/what-is-design-md) 手动整理为 Markdown 文件，放在项目根目录即可。

> 反向自动生成工具（从 Tailwind config / CSS 变量等自动生成 DESIGN.md）计划在未来提供。

### 引入后效果

- `CLAUDE.md` 中的 UI Generation Rules 会指示 agent 在生成 UI 前读取 DESIGN.md
- 设计工作流 skill 会指示 AI agent 在设计工作开始前和每个主要设计阶段读取 DESIGN.md
- 设计工作流 V2 各阶段以 DESIGN.md 为视觉身份唯一权威（SSOT），token 从中派生
- 默认只读：工作流不会静默修改 DESIGN.md；如果设计需求超出 DESIGN.md，会记录 design identity gap，并要求用户决定是收敛设计还是更新 DESIGN.md
- 没有 DESIGN.md 时，工作流退回到已有产品/设计产物；仍无项目审美输入时，才使用保守 fallback

## 使用方式

### 方式一：直接复制

```bash
# 复制单个 skill
cp -r .claude/skills/git-workflow /your-project/.claude/skills/

# 复制全部 skills
cp -r .claude/skills/* /your-project/.claude/skills/

# 复制 rules（如果需要自定义）
mkdir -p /your-project/.claude/rules
```

### 方式二：Git submodule

```bash
cd /your-project
git submodule add https://github.com/dengd1937/meridian.git .claude/meridian
```

### 方式三：手动同步

定期从本仓库拉取更新，再合并到项目自己的 `.claude/` 目录中。适合希望保留深度定制能力的团队。

## 设计原则

- Rules 已下放 — 铁律和行为护栏在 using-meridian（SessionStart hook 注入），具体规范在 skills（按需加载）和 reviewer agents（审查时强制），hooks 提供物理拦截
- 文档模板集中管理（doc-writer agent），工作流不含内联模板
- Hooks 提供确定性安全执行层（物理拦截），using-meridian 提供行为护栏

## License

MIT
