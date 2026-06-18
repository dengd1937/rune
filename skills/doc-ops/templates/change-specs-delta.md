<!-- Target: docs/changes/<feature>/specs.md | Source workflow: brainstorm Phase 5 -->

# change-specs-delta

`docs/changes/<feature>/specs.md` — 行为 delta（OpenSpec diff 格式），finishing apply 到 `docs/specs/`。

## 骨架

```markdown
# Change: <feature>

## <capability>

### Requirement: <名>
- <被删旧行为>            （- = REMOVE）
+ <新增/改后行为>          （+ = ADD / MODIFY 后）
#### Scenario: <名>
  - GIVEN ...             （无前缀 = 上下文，不改）
+ - WHEN ...
+ - THEN ...
+ #### Scenario: <新场景>   （+ 开整段 = ADD）
```

## 纪律

`+` = ADD，`-` = REMOVE，无前缀 = 上下文。按 capability 分段（每段一个受影响 capability）。finishing 的 apply：把 `+` 并入、`-` 删出对应 `docs/specs/<capability>-spec.md`。
