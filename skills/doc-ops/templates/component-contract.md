<!-- Target: docs/designs/<feature>/components/<ComponentName>.md | Source workflow: design-workflow V2-3 -->

# component-contract

`docs/designs/<feature>/components/<ComponentName>.md` — 组件契约。一个 feature 可能需要多个组件契约，每个组件一个文件。

## 骨架

```markdown
# [ComponentName]

## Variants
| Variant | Description | Visual |
|---------|-------------|--------|
| [variant] | [描述] | [截图] |

## States
| State | Trigger | Visual Change |
|-------|---------|---------------|
| [state] | [触发条件] | [视觉变化] |

## Responsive
| Breakpoint | Layout |
|-----------|--------|
| [breakpoint] | [布局描述] |

## Accessibility
- ARIA role: [角色]
- Keyboard navigation: [键盘交互]
- Focus management: [焦点管理]
- Screen reader: [屏幕阅读器行为]

## Implementation Mapping
- Base component: [基础组件来源]
- Variant system: [变体方案]
- Notes: [补充说明]

## Design Constraints
- [约束 1]
- [约束 2]

## API Notes
[仅在设计决策约束公共 API 时填写。源代码是 TypeScript props 的唯一来源。]
```
