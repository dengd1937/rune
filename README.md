# Rune

[中文文档](README.zh-CN.md)

Engineering discipline plugin for Claude Code — TDD, security review, and quality gates enforced through iron laws and hook-based interception.

## Quick Start

```bash
# Add marketplace
claude plugin marketplace add dengd1937/rune

# Install plugin
claude plugin install rune@rune
```

After installation, the following activate automatically:

- **SessionStart** hook injects iron laws on startup, clear, and compact
- **PreToolUse** hooks block dangerous commands and secret writes
- **PostToolUse** hooks detect debug statements and quality issues
- **21 skills** — invoke with `/rune:<skill-name>`
- **3 agents** — design reviewer, doc writers

## How It Works

Four enforcement layers, each with a distinct role:

```
Layer 1  Iron Laws + Routing         using-rune skill (always loaded)
Layer 2  On-Demand Guidance          21 skills (invoked when ≥1% relevant)
Layer 3  Review Enforcement          code-review skill prompt templates (during review)
Layer 4  Physical Interception       6 hooks (block at write/commit time)
```

**Iron Laws** (cannot be bypassed):

- **L1** — Each task runs its own TDD → implementation → review cycle
- **L3** — Unreviewed code cannot be committed (hook hard-block)

Chore-class changes (typos, hook regex tweaks, README edits) take a lightweight path via the `brainstorm` skill's **Scale Gate** — quality-gate, reviewer, and the commit hook still apply.

## Workflow

```
/rune:brainstorm ─→ /rune:design-workflow ─→ /rune:subagent-driven-development
  Product + Tech        UI Design                Task-by-task dev
```

| Phase | Trigger | What happens | Output |
|-------|---------|-------------|--------|
| **Brainstorm** | `/rune:brainstorm` | Product discovery, competitive research, feature analysis, technical design, spec — or Scale Gate fast-path for chore-class changes | `docs/specs/` (or skipped for chore) |
| **Design** | Auto-routes L1/L2 for UI features | Intent → wireframe → high-fidelity → review gate | `docs/designs/` |
| **Development** | Implementation phase | Research → plan → per-task TDD → quality gate → review → commit | Committed code (80%+ coverage) |

Every change starts with `/rune:brainstorm` — backend-only work skips Design, and chore-class changes (typos, hook tweaks, doc edits) take the Scale Gate fast-path: edit → quality-gate → reviewer → commit, no spec/plan written.

## Skills

| Skill | Purpose |
|-------|---------|
| [using-rune](skills/using-rune/SKILL.md) | Iron laws + skill routing — auto-loaded via SessionStart |
| [brainstorm](skills/brainstorm/SKILL.md) | Product discovery → feature spec (or Scale Gate fast-path for chore) |
| [design-workflow](skills/design-workflow/SKILL.md) | UI design — L1 lightweight / L2 full wireframe → hi-fi → review |
| [pencil-design](skills/pencil-design/SKILL.md) | Pencil MCP design + code generation |
| [writing-plans](skills/writing-plans/SKILL.md) | Implementation plans — task breakdown, no-placeholders, dual quality check |
| [subagent-driven-development](skills/subagent-driven-development/SKILL.md) | Multi-file changes — per-task TDD + review loop |
| [tdd-workflow](skills/tdd-workflow/SKILL.md) | RED → GREEN → IMPROVE cycle (80%+ coverage) |
| [investigate](skills/investigate/SKILL.md) | Root-cause analysis → TDD fix → review (no code until cause confirmed) |
| [code-quality-gate](skills/code-quality-gate/SKILL.md) | Post-edit quality gate — format, type-check, debug detection |
| [code-review](skills/code-review/SKILL.md) | Review dispatch — routes to language-specific reviewer |
| [commit-quality](skills/commit-quality/SKILL.md) | Pre-commit checks — format, lint, secrets scan |
| [review-handling](skills/review-handling/SKILL.md) | Process BLOCK feedback — deduplicate, classify, triage |
| [verifying-before-completion](skills/verifying-before-completion/SKILL.md) | Verification gate — run fresh commands before claiming success |
| [finishing-a-development-branch](skills/finishing-a-development-branch/SKILL.md) | Post-implementation — verify tests, clean artifacts, present merge options |
| [using-git-worktrees](skills/using-git-worktrees/SKILL.md) | Isolated parallel workspaces via git worktrees |
| [python-patterns](skills/python-patterns/SKILL.md) | Pythonic patterns, typing, exceptions, packaging |
| [typescript-patterns](skills/typescript-patterns/SKILL.md) | TypeScript/React patterns, shadcn/ui, Tailwind v4 |
| [django-security](skills/django-security/SKILL.md) | Django auth, CSRF/XSS/SQLi, production hardening |
| [security-reviewer](skills/security-reviewer/SKILL.md) | Security review checklist for sensitive features and pre-commit |
| [retro](skills/retro/SKILL.md) | Post-task retrospective — workflow adherence, decision quality |
| [writing-skills](skills/writing-skills/SKILL.md) | Author and maintain Rune skills |

## Agents

| Agent | Purpose | When |
|-------|---------|------|
| [design-reviewer](agents/design-reviewer.md) | Design artifact review | Design workflow steps |
| [doc-writer](agents/doc-writer.md) | Format and write workflow docs from templates | After workflow produces structured data |
| [doc-updater](agents/doc-updater.md) | Maintain catalogs, indexes, codemaps | After workflow completes |

## Hooks

| Hook | Timing | What it enforces |
|------|--------|-----------------|
| `session-start` | SessionStart | Injects iron laws via using-rune skill |
| `pre-bash-guard.sh` | PreToolUse | Blocks dangerous shell commands |
| `pre-write-secrets.sh` | PreToolUse | Blocks writes containing API keys / secrets |
| `pre-commit-review-check.py` | PreToolUse | Enforces review before git commit |
| `post-write-debug.sh` | PostToolUse | Detects leftover debug statements |
| `post-write-quality.sh` | PostToolUse | Warns on oversized files and anti-patterns |

## Directory Structure

```
rune/
├── .claude-plugin/        # Plugin manifest + marketplace entry
├── hooks/                 # Physical enforcement layer
├── skills/                # 21 auto-discovered skills
├── agents/                # 3 auto-discovered agents
├── CLAUDE.md              # Project instructions
├── README.md              # This file
└── LICENSE                # MIT
```

## License

[MIT](LICENSE)
