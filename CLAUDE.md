# Rune — Claude Code Agent Baseline

## 目录结构

```text
rune/                                  # Repo root = Plugin root
├── .claude-plugin/
│   ├── marketplace.json               # Marketplace catalog
│   └── plugin.json                    # Plugin manifest
├── hooks/
│   ├── hooks.json                     # Hook configuration（CLAUDE_PLUGIN_ROOT）
│   ├── session-start                  # 铁律注入
│   ├── pre-bash-guard.sh
│   ├── pre-write-secrets.sh
│   ├── post-write-debug.sh
│   ├── post-write-quality.sh
│   ├── pre-commit-review-check.py
│   └── lib/utils.sh
├── skills/                            # 23 skills（auto-discovered by Claude Code）
├── agents/                            # 3 agents（auto-discovered by Claude Code）
├── .claude/
│   └── settings.local.json            # Dev environment MCP permissions only
├── CLAUDE.md
├── README.md
└── LICENSE
```

## 单源结构

Repo root 即 plugin root。所有 hooks 通过 `CLAUDE_PLUGIN_ROOT` 引用路径，配置在 `hooks/hooks.json` 中。Claude Code 自动发现 `skills/` 和 `agents/` 目录。

无需双源维护，无需手动同步。

## 安装

```bash
claude plugin marketplace add dengd1937/rune
claude plugin install rune@rune
```

## 规范分层

| 层 | 内容 | 加载时机 |
|---|---|---|
| **铁律 + 路由 + 行为护栏** | using-rune skill（SessionStart hook 注入） | 始终 |
| **Skill 按需指导** | 各 skill（brainstorm、python-patterns、typescript-patterns 等） | 调用时 |
| **Agent 审查强制** | code-review skill 内置 prompt 模板（python/typescript/security） | 审查时 |
| **Hook 物理拦截** | pre-write-secrets.sh、pre-bash-guard.sh、post-write-quality.sh、pre-commit-review-check.py | 写/提交时 |
