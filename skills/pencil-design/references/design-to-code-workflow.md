# Design-to-Code Workflow

> Workflow step: **V2-3. High-Fidelity Design + Key Component Contracts**

Complete workflow for generating React + Tailwind v4 + shadcn/ui code from Pencil designs.

Target stack: React/Next.js, TypeScript, Tailwind CSS v4, shadcn/ui, Lucide icons, CVA for variants.

## Step 1: Load Aesthetic Direction

Use this priority order:

1. `DESIGN.md` in the project root, when present. It is the visual identity authority for typography, color, theme, depth, component styling, motion, spacing, and responsive behavior.
2. Existing project design artifacts: `docs/specs/`, `docs/designs/`, reusable Pencil components, and existing tokens.
3. shadcn/ui visual defaults as a conservative fallback only when no project-specific direction exists.

shadcn/ui can still be the preferred component implementation library even when DESIGN.md defines a different visual style.

Consult [tailwind-shadcn-mapping.md](tailwind-shadcn-mapping.md) for property-to-class mappings.

## Step 2: Read Design Guidelines

```javascript
pencil_get_guidelines({ topic: "code" })
pencil_get_guidelines({ topic: "tailwind" })
```

Returns rules for translating .pen design properties into code.

## Step 3: Read Design Tokens

```javascript
pencil_get_variables({ filePath: "path/to/file.pen" })
```

Map every Pencil variable to Tailwind v4 `@theme` declaration and utility class. Key principle: **Pencil variable names map 1:1 to Tailwind semantic utilities.** No arbitrary values.

See [tokens-and-variables.md](tokens-and-variables.md) for the full mapping table.

## Step 4: Read the Design Tree

```javascript
pencil_batch_get({
  filePath: "path/to/file.pen",
  nodeIds: ["screenId"],
  readDepth: 5
})
```

Use sufficient `readDepth` to see the full structure. For complex screens, read specific subtrees separately.

## Step 5: Map Components to shadcn/ui

Identify reusable components and map to shadcn/ui:

```javascript
pencil_batch_get({
  filePath: "path/to/file.pen",
  patterns: [{ reusable: true }],
  readDepth: 3
})
```

### Pencil-to-shadcn/ui Component Mapping

| Pencil Component | shadcn/ui Component | Import |
|-----------------|-------------------|--------|
| Button / Btn | `Button` | `@/components/ui/button` |
| Card / Tile / Panel | `Card`, `CardHeader`, `CardContent`, `CardFooter` | `@/components/ui/card` |
| Input / TextField | `Input` | `@/components/ui/input` |
| Select / Dropdown | `Select`, `SelectTrigger`, `SelectContent`, `SelectItem` | `@/components/ui/select` |
| Checkbox | `Checkbox` | `@/components/ui/checkbox` |
| Dialog / Modal | `Dialog`, `DialogTrigger`, `DialogContent` | `@/components/ui/dialog` |
| Tabs | `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent` | `@/components/ui/tabs` |
| Badge / Tag | `Badge` | `@/components/ui/badge` |
| Avatar | `Avatar`, `AvatarImage`, `AvatarFallback` | `@/components/ui/avatar` |
| Toast | `Toast`, `ToastAction` | `@/components/ui/toast` |
| Table | `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell` | `@/components/ui/table` |
| Alert | `Alert`, `AlertTitle`, `AlertDescription` | `@/components/ui/alert` |
| Switch / Toggle | `Switch` | `@/components/ui/switch` |
| Tooltip | `Tooltip`, `TooltipTrigger`, `TooltipContent` | `@/components/ui/tooltip` |

### Fallback Priority (When the Mapping Table Does Not Cover a Component)

Not every Pencil component has a shadcn/ui equivalent. When the table above does not cover a component, follow this priority chain in order — **do NOT skip steps and jump straight to handrolling**. Custom components are the most expensive to maintain.

| Priority | Source | When to Use | Example |
|----------|--------|-------------|---------|
| 1 | **shadcn/ui official** | Always check first | `Button`, `Card`, `Dialog` |
| 2 | **shadcn/ui registry (community)** | Official doesn't cover it; a community block does | `npx shadcn@latest add <url>` |
| 3 | **tremor** | Charts, analytics, KPIs, dashboards | `BarChart`, `AreaChart`, `Metric` |
| 4 | **magicui / aceternity-ui** | Animated sections, marketing flourishes | `AnimatedBeam`, `Meteors` |
| 5 | **Radix UI primitives** | Complex interactive widget with no higher-level component | Wrap `Radix Toolbar` with Tailwind + CVA |
| 6 | **Handroll** | **Last resort only.** Requires justification in the component spec for why options 1–5 don't fit. | Custom domain widget like `IncidentTimeline` |

#### Documenting Fallback in Component Spec

If a component falls to priority 3+, the component spec MUST include a brief justification:

```markdown
## Source
Library: tremor
Component: `BarChart`
Justification: shadcn/ui does not ship a chart component. tremor is the standard for analytics in the shadcn ecosystem.
```

For priority 6 (handroll), the justification must explicitly cite the failed alternatives:

```markdown
## Source
Handrolled
Justification:
- shadcn/ui has no timeline component
- tremor's `Tracker` displays progress, not events
- Radix does not expose a timeline primitive
- Domain semantics (incident duration, severity, operator) are too specific to reuse
```

## Step 6: Generate Code

Generate code using semantic Tailwind classes, never arbitrary values.

### Example: Button Component

```tsx
import { Button } from "@/components/ui/button"

// Never this:
<div className="bg-[#3b82f6] rounded-[6px] p-[24px]">

// Always this:
<div className="bg-primary rounded-md p-6">
```

### Example: Card with Variants

```tsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const cardVariants = cva("rounded-lg border border-border bg-card text-card-foreground shadow-sm", {
  variants: {
    variant: {
      default: "",
      destructive: "border-destructive",
      highlighted: "ring-2 ring-primary",
    },
  },
  defaultVariants: {
    variant: "default",
  },
})

interface AlertCardProps extends VariantProps<typeof cardVariants> {
  title: string
  description: string
  className?: string
}

function AlertCard({ title, description, variant, className }: AlertCardProps) {
  return (
    <Card className={cn(cardVariants({ variant }), className)}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}
```

## Step 7: Apply Visual Polish

shadcn/ui visual polish guidelines:
- Distinctive typography (not overused defaults)
- Intentional color themes (not generic AI aesthetics)
- Purposeful motion and micro-interactions
- Polished visual details

## Checklist

- [ ] Loaded the active aesthetic direction (DESIGN.md -> project artifacts -> shadcn/ui fallback)?
- [ ] Called `pencil_get_guidelines` for code and tailwind topics?
- [ ] Read design tokens with `pencil_get_variables`?
- [ ] Read design tree with `pencil_batch_get`?
- [ ] Mapped all Pencil components to shadcn/ui equivalents?
- [ ] Using semantic Tailwind classes (not arbitrary values)?
- [ ] Using CVA for component variants?
- [ ] Using `cn()` for class merging?
- [ ] Using Lucide icons (not Material Icons)?

## See Also

- [tailwind-shadcn-mapping.md](tailwind-shadcn-mapping.md) — Full property mapping tables
- [tokens-and-variables.md](tokens-and-variables.md) — Token-to-Tailwind mapping
- [responsive-breakpoints.md](responsive-breakpoints.md) — Responsive code patterns
