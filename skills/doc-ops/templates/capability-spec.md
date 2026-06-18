<!-- Target: docs/specs/<capability>-spec.md | Source workflow: brainstorm Phase 5 -->

# capability-spec

`docs/specs/<capability>-spec.md` — capability 行为契约（事实真相）。纯行为，排除实现。

一个 capability 一个文件，按系统行为域组织（如 `auth-session`、`checkout-payment`），**不按 feature 组织**。feature 是工作单元；行为变更经 `changes/<feature>/specs.md` delta 表达，finishing apply 到本文件。

## 骨架

```markdown
# [Capability] Specification

## Purpose
[一句话：这块行为管什么]

## Requirements

### Requirement: [短句，描述行为而非实现]
The system SHALL [可验证的行为]。

#### Scenario: [场景名]
- GIVEN [前置条件]
- WHEN [动作/触发]
- THEN [可观察结果]
- AND [附加断言]
```

## 纪律

- 关键字 SHALL / MUST（硬性）、SHOULD（建议）、MAY（可选）；Scenario 用 GIVEN/WHEN/THEN 且必须可验证
- **行为可入**（含错误行为，如"WHEN 无效 token THEN 返回 401"）；**实现不入**（不写 Architecture / Data Model / API 内部结构 / 技术选型——那些进 plan）
- 文件名（capability 名）即锚点；无 per-feature metadata
- 修改时**原地改到新契约**（spec 是权威，代码 conform 它），不追加 deviation
