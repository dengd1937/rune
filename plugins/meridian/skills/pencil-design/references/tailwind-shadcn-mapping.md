# Tailwind + shadcn/ui Mapping Reference

> Workflow step: **V2-3. Key Component Contracts**

Quick-reference mapping from Pencil design properties to Tailwind v4 + shadcn/ui code.

## Color Tokens

### Pencil Variable -> Tailwind Utility

| Pencil Variable | Background | Text | Border |
|----------------|-----------|------|--------|
| `primary` | `bg-primary` | `text-primary` | `border-primary` |
| `primary-foreground` | `bg-primary-foreground` | `text-primary-foreground` | - |
| `secondary` | `bg-secondary` | `text-secondary` | `border-secondary` |
| `secondary-foreground` | - | `text-secondary-foreground` | - |
| `background` | `bg-background` | - | - |
| `foreground` | - | `text-foreground` | - |
| `muted` | `bg-muted` | - | - |
| `muted-foreground` | - | `text-muted-foreground` | - |
| `accent` | `bg-accent` | - | - |
| `accent-foreground` | - | `text-accent-foreground` | - |
| `destructive` | `bg-destructive` | `text-destructive` | `border-destructive` |
| `destructive-foreground` | - | `text-destructive-foreground` | - |
| `card` | `bg-card` | - | - |
| `card-foreground` | - | `text-card-foreground` | - |
| `border` | - | - | `border-border` |
| `ring` | - | - | `ring-ring` |

**`@theme` rule**: All color variables use `--color-` prefix: `--color-primary`, `--color-border`, etc.

### Common Combinations

| Design Intent | Tailwind Classes |
|--------------|-----------------|
| Primary button | `bg-primary text-primary-foreground` |
| Secondary button | `bg-secondary text-secondary-foreground` |
| Destructive button | `bg-destructive text-destructive-foreground` |
| Ghost button | `hover:bg-accent hover:text-accent-foreground` |
| Outline button | `border border-border bg-background hover:bg-accent` |
| Card surface | `bg-card text-card-foreground border border-border` |
| Muted text | `text-muted-foreground` |
| Page background | `bg-background text-foreground` |
| Input field | `border border-border bg-background text-foreground placeholder:text-muted-foreground` |

## Radius Tokens

| Pencil Variable | `@theme` Declaration | Tailwind Utility |
|----------------|---------------------|------------------|
| `radius-sm` | `--radius-sm: 0.25rem` | `rounded-sm` |
| `radius-md` | `--radius-md: 0.375rem` | `rounded-md` |
| `radius-lg` | `--radius-lg: 0.5rem` | `rounded-lg` |
| `radius-xl` | `--radius-xl: 0.75rem` | `rounded-xl` |

## Layout Properties

| Pencil Property | Tailwind Class |
|----------------|----------------|
| `layout: "vertical"` | `flex flex-col` |
| `layout: "horizontal"` | `flex` or `flex flex-row` |
| `gap: 4` | `gap-1` |
| `gap: 8` | `gap-2` |
| `gap: 12` | `gap-3` |
| `gap: 16` | `gap-4` |
| `gap: 20` | `gap-5` |
| `gap: 24` | `gap-6` |
| `gap: 32` | `gap-8` |
| `padding: 8` | `p-2` |
| `padding: 12` | `p-3` |
| `padding: 16` | `p-4` |
| `padding: 20` | `p-5` |
| `padding: 24` | `p-6` |
| `padding: 32` | `p-8` |
| `width: "fill_container"` | `w-full` |
| `height: "fill_container"` | `h-full` or `flex-1` |
| `alignItems: "center"` | `items-center` |
| `alignItems: "start"` | `items-start` |
| `alignItems: "end"` | `items-end` |
| `justifyContent: "center"` | `justify-center` |
| `justifyContent: "space-between"` | `justify-between` |
| `justifyContent: "end"` | `justify-end` |

## Typography

| Pencil Property | Tailwind Class |
|----------------|----------------|
| `fontSize: 12` | `text-xs` |
| `fontSize: 14` | `text-sm` |
| `fontSize: 16` | `text-base` |
| `fontSize: 18` | `text-lg` |
| `fontSize: 20` | `text-xl` |
| `fontSize: 24` | `text-2xl` |
| `fontSize: 30` | `text-3xl` |
| `fontSize: 36` | `text-4xl` |
| `fontSize: 48` | `text-5xl` |
| `fontWeight: "400"` | `font-normal` |
| `fontWeight: "500"` | `font-medium` |
| `fontWeight: "600"` | `font-semibold` |
| `fontWeight: "700"` | `font-bold` |

## Pencil Component -> shadcn/ui Mapping

| Pencil Component | shadcn/ui | Key Classes |
|-----------------|-----------|-------------|
| Button | `Button` | `bg-primary text-primary-foreground rounded-md` |
| Card | `Card` | `rounded-lg border border-border bg-card text-card-foreground shadow-sm` |
| Input | `Input` | `rounded-md border border-border bg-background` |
| Select | `Select` | `border border-border bg-background` |
| Checkbox | `Checkbox` | `border-border` |
| Badge | `Badge` | `bg-primary text-primary-foreground rounded-full` |
| Alert | `Alert` | `rounded-lg border bg-background p-4` |
| Dialog | `Dialog` | `rounded-lg border bg-background shadow-lg` |
| Table | `Table` | `w-full caption-bottom text-sm` |
| Tabs | `Tabs` | `border-b border-border` |
| Tooltip | `Tooltip` | `rounded-md bg-primary text-primary-foreground` |

## Anti-Patterns

| Never | Use Instead |
|-------|-------------|
| `bg-[#3b82f6]` | `bg-primary` |
| `text-[#ffffff]` | `text-primary-foreground` |
| `text-[var(--primary)]` | `text-primary` |
| `rounded-[6px]` | `rounded-md` |
| `border-[#e2e8f0]` | `border-border` |
| `tailwind.config.ts` | CSS `@theme` block (Tailwind v4) |
| Material Icons | Lucide React icons |

## See Also

- [tokens-and-variables.md](tokens-and-variables.md) — Token mapping pipeline
- [design-to-code-workflow.md](design-to-code-workflow.md) — Complete code generation workflow
- [responsive-breakpoints.md](responsive-breakpoints.md) — Responsive patterns
