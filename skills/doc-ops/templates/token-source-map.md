<!-- Target: docs/designs/<feature>/tokens/source-map.md | Source workflow: design-workflow V2-2 / V2-3 -->

# token-source-map

`docs/designs/<feature>/tokens/source-map.md` — token 来源追踪。

## 骨架

```markdown
# Token Source Map

## 来源规则

| Source | 含义 |
|---|---|
| DESIGN.md | 来自项目根目录 DESIGN.md |
| existing Pencil variable | 来自已有 Pencil 变量 |
| existing code token | 来自已有代码 token |
| fallback | DESIGN.md 缺失该规则时的保守默认值 |
| user decision | 用户明确批准的新视觉身份规则 |

## Tokens

| Token | Value | Source | Source Detail | Rationale |
|---|---:|---|---|---|
| [token] | [value] | [source] | [section / variable / file] | [why this source is valid] |

## Design Identity Gaps

- [gap]：[是否已由用户决策解决]
```
