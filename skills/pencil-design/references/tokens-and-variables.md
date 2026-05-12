# Variables and Design Tokens

> Workflow step: **V2-2 / V2-3. Design Tokens**

Covers reading, creating, and mapping Pencil variables to the Style Dictionary token pipeline.

## Deriving Tokens from DESIGN.md

When `DESIGN.md` exists in the project root, baseline tokens are derived from it rather than invented. The following table maps each DESIGN.md section to its corresponding token category.

### Mapping Table

| DESIGN.md Section | Token Category | Derivation Rule |
|---|---|---|
| Color palette and roles | Brand / Semantic / Surface / UI colors | Each named color with its hex value maps to a Pencil variable. Use the semantic name from DESIGN.md (e.g., "brand accent" → `accent`). |
| Typography rules | `font-sans`, `font-mono`, `font-heading`, `text-*` | Font family → `font-*` variables. Size hierarchy → `text-xs/sm/base/lg/xl` scale. Weight, line-height, and letter-spacing are applied at the component level. |
| Layout principles | `spacing-*`, `radius-*`, `breakpoint-*` | Base unit and spacing scale → `spacing-xs` through `spacing-2xl`. Border-radius scale → `radius-sm/md/lg/xl`. Container width → `breakpoint-*`. |
| Depth and elevation | `shadow-*` | Each shadow level maps to `shadow-sm/md/lg/xl` with the specified rgba values. |
| Component styles | Component-level token defaults | Padding, border-radius, font-size per component serve as defaults when building wireframes. |
| Visual theme and atmosphere | *Context reference only* | Not tokenized. Used as ambient context to guide design decisions (e.g., "minimalism as engineering principle" informs spacing and decoration choices). |
| Do's and don'ts | *Constraint layer* | Not tokenized. Applied as validation rules during V2-3 and V2-4. |
| Responsive behavior | `breakpoint-*`, touch target constraints | Breakpoint values → `breakpoint-sm/md/lg/xl`. Touch target minimum noted for component padding. |
| Agent prompt guide | *Context reference only* | Not tokenized. Quick-reference color summary used for fast agent reads. |

### Priority

When DESIGN.md exists: **DESIGN.md values > existing Pencil variables > defaults**.

If a DESIGN.md value conflicts with an existing Pencil variable, use the DESIGN.md value and update the variable via `pencil_set_variables`.

Every token decision must record provenance in `docs/designs/<feature>/tokens/source-map.md`. This gives reviewers evidence for whether a token came from DESIGN.md, an existing Pencil variable, or a fallback default.

### Token Source Map

Create or update `docs/designs/<feature>/tokens/source-map.md` whenever baseline tokens are created or expanded.

```markdown
# Token Source Map

| Token | Value | Source | Source Detail | Rationale |
|---|---:|---|---|---|
| primary | #3b82f6 | DESIGN.md | Color palette and roles / primary action | Primary action color defined by visual identity |
| radius-md | 6px | existing Pencil variable | `radius-md` | Matches existing component system |
| shadow-sm | 0 1px 2px rgba(...) | fallback | shadcn/ui default | DESIGN.md has no elevation rule; conservative fallback pending user decision |
```

Source must be one of:

- `DESIGN.md`
- `existing Pencil variable`
- `existing code token`
- `fallback`
- `user decision`

If `Source` is `fallback`, the rationale must identify the DESIGN.md gap and should be resolved before Gate 3 when the token materially affects brand identity.

Always read tokens at the start of any design task:

```javascript
pencil_get_variables({ filePath: "path/to/file.pen" })
```

Returns flat key-value pairs:

```json
{
  "variables": {
    "primary": { "value": "#3b82f6" },
    "primary-foreground": { "value": "#ffffff" },
    "background": { "value": "#ffffff" },
    "foreground": { "value": "#0a0a0a" },
    "border": { "value": "#e2e8f0" },
    "radius-sm": { "value": 4 },
    "radius-md": { "value": 6 },
    "radius-lg": { "value": 8 }
  }
}
```

## Naming Convention

All tokens across all features MUST follow this canonical naming convention. This prevents token name drift (e.g., `primary` vs `brand` vs `color-primary`) that fragments the design system.

### Rules

1. **kebab-case only** — use hyphens as separators. Never camelCase or snake_case.
2. **Semantic names, not visual names** — `primary` not `blue`, `destructive` not `red`, `muted-foreground` not `gray-500`.
3. **Foreground pairs use `-foreground` suffix** — `primary` + `primary-foreground`, `card` + `card-foreground`. Never `primary-text` or `on-primary`.
4. **Scale uses `-sm/md/lg/xl` suffix** — `radius-md`, `spacing-lg`, `shadow-sm`. Never `radius-medium` or `radius2`.
5. **Prefix by category for non-color tokens** — `radius-*`, `spacing-*`, `shadow-*`, `font-*`, `text-*`, `breakpoint-*`. Colors are the exception: they use the semantic name directly (`primary`, not `color-primary`).
6. **Never use feature-specific names** — a token in `docs/designs/alerts/` named `alert-red` is wrong. Use a shared `destructive` token instead.

### Canonical Names Reference

| Category | Token Name | Purpose |
|----------|-----------|---------|
| Brand color | `primary` | Primary brand color |
| Brand color | `primary-foreground` | Text/icon color on primary background |
| Brand color | `secondary` | Secondary brand color |
| Brand color | `secondary-foreground` | Text/icon color on secondary background |
| Brand color | `accent` | Accent highlight color |
| Brand color | `accent-foreground` | Text/icon color on accent background |
| Semantic color | `destructive` | Error, delete, dangerous action |
| Semantic color | `destructive-foreground` | Text/icon color on destructive background |
| Semantic color | `success` | Confirmation, completed state |
| Semantic color | `success-foreground` | Text/icon color on success background |
| Semantic color | `warning` | Caution, attention |
| Semantic color | `warning-foreground` | Text/icon color on warning background |
| Surface color | `background` | Default page background |
| Surface color | `foreground` | Default text color on background |
| Surface color | `card` | Card / elevated surface background |
| Surface color | `card-foreground` | Text color on card background |
| Surface color | `popover` | Popover / tooltip / menu background |
| Surface color | `popover-foreground` | Text color on popover background |
| Surface color | `muted` | Subdued background (disabled, placeholder area) |
| Surface color | `muted-foreground` | Subdued text color |
| UI color | `border` | Default border color |
| UI color | `input` | Form input border color |
| UI color | `ring` | Focus ring color |
| Typography | `font-sans` | Default sans-serif family |
| Typography | `font-mono` | Monospace family |
| Typography | `font-heading` | Heading family (if distinct from sans) |
| Typography | `text-xs` / `text-sm` / `text-base` / `text-lg` / `text-xl` | Font size scale |
| Border radius | `radius-sm` / `radius-md` / `radius-lg` / `radius-xl` | Border radius scale |
| Spacing | `spacing-xs` / `spacing-sm` / `spacing-md` / `spacing-lg` / `spacing-xl` / `spacing-2xl` | Spacing scale |
| Shadow | `shadow-sm` / `shadow-md` / `shadow-lg` / `shadow-xl` | Elevation scale |
| Breakpoint | `breakpoint-sm` / `breakpoint-md` / `breakpoint-lg` / `breakpoint-xl` | Responsive thresholds |

### Forbidden Names

| Bad | Why | Use Instead |
|-----|-----|-------------|
| `brand-primary` | Redundant prefix | `primary` |
| `color-primary` | Category prefix not used for colors | `primary` |
| `primary-text` | Wrong foreground convention | `primary-foreground` |
| `on-primary` | Material Design convention, not shadcn | `primary-foreground` |
| `red-500` | Visual name, not semantic | `destructive` |
| `radius-medium` | Use scale suffix | `radius-md` |
| `gray-bg` | Not semantic | `muted` |
| `alert-red` | Feature-specific color | `destructive` |
| `dashboard-header-bg` | Feature-specific surface | `card` or create a shared surface token |

---

## Creating Variables

Define the visual foundation for the design:

```javascript
pencil_set_variables({
  filePath: "path/to/file.pen",
  variables: {
    "primary": { "value": "#3b82f6" },
    "primary-foreground": { "value": "#ffffff" },
    "secondary": { "value": "#64748b" },
    "accent": { "value": "#f59e0b" },
    "radius-md": { "value": 6 },
    "radius-lg": { "value": 8 }
  }
})
```

### Required Token Categories

| Category | Variables | Example Values |
|----------|-----------|----------------|
| Brand colors | `primary`, `secondary`, `accent` | `#3b82f6`, `#64748b`, `#f59e0b` |
| Semantic colors | `destructive`, `success`, `warning` | `#ef4444`, `#22c55e`, `#f59e0b` |
| Surface colors | `background`, `foreground`, `card`, `card-foreground` | `#ffffff`, `#0a0a0a` |
| UI colors | `border`, `ring`, `muted`, `muted-foreground` | `#e2e8f0`, `#94a3b8` |
| Border radius | `radius-sm`, `radius-md`, `radius-lg`, `radius-xl` | `4`, `6`, `8`, `12` |
| Typography | `font-sans`, `font-mono`, `font-heading` | `Inter, sans-serif` |
| Spacing | `spacing-xs`, `spacing-sm`, `spacing-md`, `spacing-lg` | `4`, `8`, `16`, `24` |

## Theme Support

Variables can have different values per theme (light/dark):

```json
{
  "primary": {
    "themes": {
      "light": "#3b82f6",
      "dark": "#60a5fa"
    }
  }
}
```

## Style Dictionary Token Pipeline

Pencil exports flat key-value pairs. The design-workflow.md token pipeline converts them:

```
pencil_get_variables
        | flat key-value (e.g., "primary": "#3b82f6")
scripts/tokens-convert.ts
        | Pencil flat -> W3C DTCG JSON
docs/designs/<feature>/tokens/w3c.json
        |
Style Dictionary + style-dictionary-utils
        | build
  +-- tokens.css              (--color-primary: #3b82f6; ...)
  +-- tokens.ts               (typed constant references)
  +-- tailwind-preset.ts      (Tailwind v4 plugin with @theme declarations)
  +-- source-map.md           (human-readable token provenance)
```

### W3C DTCG Intermediate Format

The conversion script produces W3C DTCG standard format:

```json
{
  "color": {
    "primary": { "$value": "#3b82f6", "$type": "color" },
    "success": { "$value": "#22c55e", "$type": "color" }
  },
  "spacing": {
    "md": { "$value": "1rem", "$type": "dimension" }
  },
  "border": {
    "radius": {
      "md": { "$value": "0.375rem", "$type": "dimension" }
    }
  }
}
```

### Conversion Rules

| Pencil variable pattern | W3C `$type` | Example |
|------------------------|-------------|---------|
| Hex color values (`#...`) | `color` | `"primary": "#3b82f6"` -> `$type: "color"` |
| Values with rem/px units | `dimension` | `"radius-md": "0.375rem"` -> `$type: "dimension"` |
| Font family values | `fontFamily` | `"font-sans": "Inter, sans-serif"` -> `$type: "fontFamily"` |
| Numeric-only values | `number` | `"font-weight-normal": "400"` -> `$type: "number"` |

## Tailwind v4 Mapping

Pencil variables map 1:1 to Tailwind v4 semantic utilities. Never use arbitrary values.

### Color Mapping

| Pencil Variable | `@theme` Declaration | Tailwind Utility |
|----------------|---------------------|------------------|
| `primary` | `--color-primary` | `bg-primary`, `text-primary`, `border-primary` |
| `primary-foreground` | `--color-primary-foreground` | `text-primary-foreground` |
| `background` | `--color-background` | `bg-background` |
| `foreground` | `--color-foreground` | `text-foreground` |
| `border` | `--color-border` | `border-border` |
| `muted` | `--color-muted` | `bg-muted` |
| `muted-foreground` | `--color-muted-foreground` | `text-muted-foreground` |
| `destructive` | `--color-destructive` | `bg-destructive`, `text-destructive` |

### Radius Mapping

| Pencil Variable | `@theme` Declaration | Tailwind Utility |
|----------------|---------------------|------------------|
| `radius-sm` | `--radius-sm: 0.25rem` | `rounded-sm` |
| `radius-md` | `--radius-md: 0.375rem` | `rounded-md` |
| `radius-lg` | `--radius-lg: 0.5rem` | `rounded-lg` |
| `radius-xl` | `--radius-xl: 0.75rem` | `rounded-xl` |

## What NEVER to Generate

| Bad (arbitrary values) | Good (semantic utilities) |
|----------------------|--------------------------|
| `bg-[#3b82f6]` | `bg-primary` |
| `text-[#ffffff]` | `text-primary-foreground` |
| `text-[var(--primary)]` | `text-primary` |
| `rounded-[6px]` | `rounded-md` |
| `rounded-[var(--radius-md)]` | `rounded-md` |
| `border-[#e2e8f0]` | `border-border` |

## Checklist

- [ ] Called `pencil_get_variables` to see available tokens?
- [ ] Using variable references instead of hardcoded values?
- [ ] If needed variable doesn't exist, created it with `pencil_set_variables`?
- [ ] Updated `tokens/source-map.md` for every new or changed token?
- [ ] For code generation: using semantic Tailwind classes, NOT arbitrary values?

## See Also

- [tailwind-shadcn-mapping.md](tailwind-shadcn-mapping.md) — Full mapping tables
- [design-to-code-workflow.md](design-to-code-workflow.md) — Code generation using tokens
