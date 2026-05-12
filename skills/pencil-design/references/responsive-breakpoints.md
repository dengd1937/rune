# Responsive Breakpoints

> Workflow step: **V2-3. Key Component Contracts**

Mapping Pencil multi-artboard designs to Tailwind CSS responsive breakpoints.

## Pencil Artboard Sizes -> Tailwind Breakpoints

### Standard Artboard Widths

| Device | Pencil Artboard Width | Tailwind Breakpoint | Prefix |
|--------|----------------------|--------------------|----|
| Mobile (small) | 320px | Default (no prefix) | - |
| Mobile (standard) | 375px | Default (no prefix) | - |
| Mobile (large) | 393-430px | Default (no prefix) | - |
| Tablet (portrait) | 768px | `md` | `md:` |
| Tablet (landscape) | 1024px | `lg` | `lg:` |
| Desktop | 1280px | `xl` | `xl:` |
| Desktop (wide) | 1440px | `2xl` | `2xl:` |

### Tailwind v4 Breakpoint Values

Default breakpoints (built into Tailwind, no `@theme` needed):

```css
sm -> 640px
md -> 768px
lg -> 1024px
xl -> 1280px
2xl -> 1536px
```

Custom breakpoints use `@theme`:

```css
@theme {
  --breakpoint-xs: 475px;
  --breakpoint-3xl: 1920px;
}
```

## Multi-Artboard Design to Code

### Reading Multiple Artboards

```javascript
// Find all screen artboards
pencil_batch_get({
  filePath: "path/to/file.pen",
  patterns: [{ type: "frame", name: "Mobile|Tablet|Desktop" }],
  readDepth: 4
})

// Or read top-level nodes to identify all screens
pencil_batch_get({ filePath: "path/to/file.pen" })
```

### Code Generation Strategy

Generate **mobile-first**, then add breakpoint overrides:

```tsx
// Mobile-first: base styles = mobile artboard
// md: styles = tablet artboard
// lg: styles = desktop artboard
<div className="flex flex-col lg:flex-row">
  <aside className="hidden lg:block lg:w-64">
    {/* Sidebar: hidden on mobile, visible on desktop */}
  </aside>
  <main className="w-full lg:flex-1">
    {/* Main content: full width on mobile, flexible on desktop */}
  </main>
</div>
```

## Common Responsive Patterns

| Pencil Design Pattern | Tailwind Implementation |
|----------------------|------------------------|
| 1 col -> 2 cols -> 3 cols | `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3` |
| Stacked sidebar -> side-by-side | `flex flex-col lg:flex-row` |
| Hidden on mobile, visible desktop | `hidden lg:block` |
| Visible mobile, hidden desktop | `block lg:hidden` |
| Full-width mobile, constrained desktop | `w-full max-w-7xl mx-auto` |
| Small text mobile, larger desktop | `text-sm md:text-base lg:text-lg` |
| Less padding mobile, more desktop | `p-4 md:p-6 lg:p-8` |
| Card grid responsive | `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6` |

## Layout Differences Between Artboards

| What Changes | Mobile Artboard | Desktop Artboard | Code Pattern |
|-------------|----------------|-----------------|--------------|
| Layout direction | `layout: "vertical"` | `layout: "horizontal"` | `flex flex-col lg:flex-row` |
| Column count | 1 column | 2-4 columns | `grid-cols-1 lg:grid-cols-3` |
| Visibility | Element missing | Element present | `hidden lg:block` |
| Font size | Smaller | Larger | `text-2xl lg:text-4xl` |
| Padding | 16px | 24-32px | `p-4 lg:p-8` |
| Gap | 16px | 24px | `gap-4 lg:gap-6` |
| Sidebar | Hidden or stacked | Side-by-side | `hidden lg:block lg:w-64` |
| Image size | Smaller/cropped | Full size | `h-48 lg:h-80` |

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| Hardcoding pixel widths from artboard | Use Tailwind breakpoints + responsive utilities |
| Separate mobile/desktop components | One component with responsive classes |
| `max-width` media queries | Mobile-first with `min-width` (Tailwind default) |
| Ignoring mobile artboard | Start from mobile, add `md:` / `lg:` overrides |
| `@media` in CSS for breakpoints | Tailwind responsive prefixes in className |
| `w-[375px]` from mobile artboard | `w-full` with responsive max-width |
| `w-[1440px]` from desktop artboard | `max-w-7xl mx-auto` or similar |

## Container Queries (Advanced)

For component-level responsiveness (adapts to container, not viewport):

```css
@theme {
  /* No setup needed -- Tailwind v4 supports @container natively */
}
```

```tsx
{/* Responds to parent container width, not viewport */}
<div className="@container">
  <div className="grid grid-cols-1 @md:grid-cols-2 @lg:grid-cols-3">
    {/* ... */}
  </div>
</div>
```

Use container queries when the same component appears in different contexts (sidebar vs main content).

## Checklist

- [ ] Identified all artboard sizes and mapped to Tailwind breakpoints?
- [ ] Generating mobile-first code (base = mobile artboard)?
- [ ] Using breakpoint prefixes (`md:`, `lg:`) for tablet/desktop?
- [ ] Compared artboards to identify what changes between sizes?
- [ ] Using `grid-cols-*` with breakpoint prefixes for column changes?
- [ ] Using `hidden`/`block` with breakpoint prefixes for visibility?
- [ ] Avoiding hardcoded pixel widths from artboard dimensions?

## See Also

- [wireframe-and-layout.md](wireframe-and-layout.md) — Layout construction patterns
- [design-to-code-workflow.md](design-to-code-workflow.md) — Complete code generation workflow
