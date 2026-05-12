# DESIGN.md Preflight

> Workflow step: **V2-1. Design Intent**

Use this preflight before treating `DESIGN.md` as the visual identity authority. The goal is not to reject imperfect files; it is to surface missing identity decisions before the agent invents them.

## Required Sections

Check whether `DESIGN.md` contains these 9 modules:

1. Visual theme and atmosphere
2. Color palette and roles
3. Typography rules
4. Layout principles
5. Depth and elevation
6. Component styles
7. Do's and don'ts
8. Responsive behavior
9. Agent prompt guide

## Minimum Useful Content

The file is usable as a strong visual authority when it includes:

- At least one primary/accent color role and core surface/text colors
- Font family or typography hierarchy
- Spacing and radius principles
- Component style direction for common surfaces and controls
- Responsive behavior for mobile and desktop
- Explicit do's and don'ts

## Classification

| Result | Meaning | Workflow Behavior |
|---|---|---|
| Complete | All required modules exist and minimum content is present | Treat DESIGN.md as visual identity SSOT |
| Partial | Some modules or minimum content are missing | Use present sections as constraints; record missing sections as design identity gaps |
| Invalid | File is empty, unrelated, or internally contradictory | Do not treat as SSOT; ask user to provide or fix DESIGN.md |

## Gap Handling

When a gap is found:

1. Record it in `docs/designs/<feature>/intent.md`.
2. Do not invent a new visual rule silently.
3. Default to constraining the design to the existing DESIGN.md sections.
4. If the feature genuinely needs a new visual identity rule, ask the user whether to update DESIGN.md.

## Output Data

Pass this summary to `doc-writer` when writing `design-intent`:

```markdown
## DESIGN.md Preflight

**Status:** Complete / Partial / Invalid / Not present

**Usable Sections:**
- [section]: [how it constrains this feature]

**Design Identity Gaps:**
- [gap]: [why it matters and what user decision is needed]

**Decision:**
[Use as SSOT / Use partial constraints / Wait for user update / Proceed without DESIGN.md]
```
