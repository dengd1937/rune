# 代码审查规范

## 何时审查

> Commit 前提醒: `pre-commit-review-check.py`

**强制触发**（commit 前 / merge 前）：
- 向共享分支提交任何 commit 前
- 安全敏感代码变更时（auth、支付、用户数据）
- 合并 pull request 前

**建议触发**：写完或修改代码后、架构变更时

**审查前提**：CI/CD 通过、merge 冲突已解决、分支已同步

## 严重等级

| 等级 | 含义 | 处理方式 |
|------|------|---------|
| CRITICAL | 安全漏洞或数据丢失风险 | **阻塞** — merge 前必须修复 |
| HIGH | Bug 或重大质量问题 | **警告** — 建议 merge 前修复 |
| MEDIUM | 可维护性问题 | **提示** — 考虑修复 |
| LOW | 风格或次要建议 | **备注** — 可选 |

## Agent 使用

| Agent | 用途 |
|-------|------|
| **task-driven-development skill** | 通用代码质量审查（Step 4 通过 general-purpose + code-quality-reviewer-prompt.md） |
| **security-reviewer** | 安全漏洞、OWASP Top 10（Step 4 并发触发） |
| **python-reviewer** | Python 专项问题（Step 4 并发触发） |
| **typescript-reviewer** | TypeScript/React 类型安全、异步模式、hooks（Step 4 并发触发） |
| **code-reviewer** | [已废弃] 由 task-driven-development skill 内部 prompt 模板替代 |

## 审批标准（人类 PR 审查语境）

- **通过**：无 CRITICAL 或 HIGH 问题
- **警告**：仅有 HIGH 问题（谨慎合并）
- **阻塞**：发现 CRITICAL 问题

> **注：语境差异。** 上述三态语义用于**人类 PR 审查**。
> 在 `task-driven-development` skill（AI 自动化流程）内 HIGH 被收紧为 BLOCK，
> 改为二态（APPROVE / BLOCK），原因是 AI 流程没有人类把关、宁严勿宽。
> 详见 `.claude/skills/task-driven-development/code-quality-reviewer-prompt.md`。

→ code-quality-gate skill / security-reviewer agent

## Red Flags — 跳过审查的合理化借口

| 借口 | 现实 |
|---|---|
| "代码看起来挺干净，应该没问题" | 没经过 reviewer agent = 没审查；自我感觉不算 |
| "我自己审过了，不用再叫 agent" | 自审有确认偏差；reviewer agent 是独立第二意见 |
| "改动很小，CRITICAL 不可能存在" | 一行改动就能引入 SQL 注入、原型污染、TOCTOU |
| "改动不涉及安全敏感代码" | auth/输入/支付/外部 API/文件系统 都触发 security-reviewer，自判"敏感"易漏 |
| "Python/TS 项目用通用 code-reviewer 就够" | 语言专项审查（python-reviewer/typescript-reviewer）必须叠加，不可替代 |
| "刚刚审过类似改动" | 每个 commit 必须独立审查；上次的审查不覆盖这次 |
| "review 中 CRITICAL 等会再修" | CRITICAL 阻塞 commit，必须**先**修 |
| "HIGH 问题先合进去再开 issue" | HIGH 是警告级，需谨慎合并并明确记录原因，不是默认放行 |
| "reviewer 误报了" | 误报需说明具体理由并由用户确认；不允许模型自行驳回 |
