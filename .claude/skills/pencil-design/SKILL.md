---
name: pencil-design
description: Design UIs in Pencil (.pen files) and generate production code. Activates for tasks involving Pencil MCP tools, .pen files, design-to-code workflows, or UI design with Pencil. Integrates with the design-workflow.md v2 stages for wireframing, token work, and high-fidelity design.
metadata:
  author: sre-copilot
  version: "1.0"
  references:
    - chiroro-jr/pencil-design-sskill (MIT)
    - partme-ai/pencil-skills (Apache 2.0)
---

# Pencil Design Skill

Design production-quality UIs in Pencil and generate clean, maintainable code from them. This skill provides the execution layer for the [design workflow](/.claude/skills/design-workflow/SKILL.md) stages `V2-2` and `V2-3`.

## When to Use This Skill

- Designing screens, pages, or components in a `.pen` file
- Generating code (React, Next.js, TypeScript) from Pencil designs
- Building or extending a design system in Pencil
- Managing design tokens between Pencil and code
- Working with any Pencil MCP tools

## Design Workflow Alignment

This skill is the execution layer for the design workflow. Each reference document maps to a workflow step:

| Workflow Step | Reference Document |
|---------------|-------------------|
| V2-2. Wireframe + Baseline Tokens | [wireframe-and-layout.md](references/wireframe-and-layout.md) |
| V2-2 / V2-4. Visual Verification | [visual-verification.md](references/visual-verification.md) |
| V2-2 / V2-3. Design Tokens | [tokens-and-variables.md](references/tokens-and-variables.md) |
| V2-3. Key Component Contracts | [component-specification.md](references/component-specification.md) |
| V2-3. Design-to-Code | [design-to-code-workflow.md](references/design-to-code-workflow.md) |
| V2-3. Component Mapping | [tailwind-shadcn-mapping.md](references/tailwind-shadcn-mapping.md) |
| V2-3. Responsive Layout | [responsive-breakpoints.md](references/responsive-breakpoints.md) |

## Critical Rules

These rules address the most common agent mistakes. Violating them produces designs that are inconsistent, hard to maintain, and generate poor code.

### Rule 1: Always Reuse Design System Components

**NEVER recreate a component from scratch when one already exists in the design file.**

Before inserting any element:

1. Call `pencil_batch_get` with `patterns: [{ reusable: true }]` to list available components
2. Search results for a matching component (button, card, input, nav, etc.)
3. If a match exists, insert as a `ref` instance: `I(parent, { type: "ref", ref: "componentId" })`
4. Customize via descendant updates: `U(instanceId + "/childId", { ... })`
5. Only create from scratch if no suitable component exists

See [wireframe-and-layout.md](references/wireframe-and-layout.md) for detailed workflow.

### Rule 2: Always Use Variables Instead of Hardcoded Values

**NEVER hardcode colors, border radius, spacing, or typography values when variables exist.**

Before applying any style:

1. Call `pencil_get_variables` to read defined design tokens
2. Map intended values to existing variables (`primary` not `#3b82f6`, `radius-md` not `6`)
3. When generating code, use semantic Tailwind classes (`bg-primary`, `rounded-md`), never arbitrary values (`bg-[#3b82f6]`, `rounded-[6px]`)

See [tokens-and-variables.md](references/tokens-and-variables.md) for detailed token mapping.

### Rule 3: Prevent Text and Content Overflow

**NEVER allow text or child elements to overflow their parent or the artboard.**

1. Set text width to `fill_container` inside auto-layout frames
2. Use `maxLines` for text that should truncate
3. After inserting content, call `pencil_snapshot_layout` with `problemsOnly: true`
4. Fix any reported issues before proceeding

See [wireframe-and-layout.md](references/wireframe-and-layout.md) for overflow prevention patterns.

### Rule 4: Visually Verify Every Section

**NEVER skip visual verification after building a section or screen.**

After each logical section:

1. Call `pencil_get_screenshot` on the section node
2. Analyze for alignment, spacing, text overflow, visual glitches
3. Call `pencil_snapshot_layout` with `problemsOnly: true`
4. Fix issues before moving to the next section

See [visual-verification.md](references/visual-verification.md) for verification workflow.

### Rule 5: Reuse Existing Assets

**NEVER generate a new logo or duplicate asset when one already exists.**

1. Search existing image/logo nodes by name pattern
2. If found, copy with `C()` operation
3. Only use `G()` (Generate) for genuinely new images
4. Logos: always copy from existing instance, never regenerate

### Rule 6: Use the Active Aesthetic Direction

**NEVER design in Pencil or generate code without aesthetic direction.**

Priority:

1. If `DESIGN.md` exists, use it as the visual identity authority for typography, color, theme, motion, spacing, and component style decisions.
2. If `DESIGN.md` does not exist, use the existing product/design docs and reusable Pencil components as the local direction.
3. If no project-specific direction exists, use shadcn/ui default aesthetics as the conservative fallback.

shadcn/ui can remain the preferred implementation library even when it is not the aesthetic authority.

Consult [tailwind-shadcn-mapping.md](references/tailwind-shadcn-mapping.md) for property-to-class mappings.

## MCP Tool Quick Reference

| Tool | When to Use |
|------|-------------|
| `pencil_get_editor_state` | First call - understand file state and get .pen schema |
| `pencil_batch_get` | Read nodes, search components (`reusable: true`), inspect structure |
| `pencil_batch_design` | Insert, copy, update, replace, move, delete elements; generate images |
| `pencil_get_variables` | Read design tokens (colors, radius, spacing, fonts) |
| `pencil_set_variables` | Create or update design tokens |
| `pencil_get_screenshot` | Visual verification of any node |
| `pencil_snapshot_layout` | Detect clipping, overflow, overlapping elements |
| `pencil_get_guidelines` | Design rules for: `code`, `table`, `tailwind`, `landing-page`, `design-system` |
| `pencil_find_empty_space_on_canvas` | Find space for new screens/frames |
| `pencil_get_style_guide_tags` | Browse available style directions |
| `pencil_get_style_guide` | Get specific style inspiration |
| `pencil_search_all_unique_properties` | Audit property values across the document |
| `pencil_replace_all_matching_properties` | Bulk update properties (e.g., swap colors) |
| `pencil_open_document` | Open a .pen file or create a new document |

## Workflow Summary

### Wireframe + Baseline Tokens (V2-2)

```
1. pencil_get_editor_state        -> Understand file state
2. pencil_batch_get (reusable)    -> Discover components
3. pencil_get_variables           -> Read design tokens
4. pencil_get_guidelines          -> Get design rules
5. pencil_find_empty_space_on_canvas -> Find space
6. pencil_batch_design            -> Build section by section
7. pencil_get_screenshot          -> Verify each section
8. pencil_snapshot_layout         -> Check for problems
```

### Token Pipeline (V2-3)

```
1. pencil_set_variables           -> Define tokens in Pencil
2. pencil_get_variables           -> Export flat key-value pairs
3. scripts/tokens-convert.ts      -> Convert to W3C DTCG JSON
4. Style Dictionary build         -> Generate CSS/TS/Tailwind outputs
```

See [tokens-and-variables.md](references/tokens-and-variables.md) for full pipeline details.

### Design-to-Code (V2-3)

```
1. Load the active aesthetic direction (DESIGN.md -> project docs/components -> shadcn/ui fallback)
2. pencil_get_guidelines (code, tailwind) -> Get code generation rules
3. pencil_get_variables -> Map tokens to Tailwind @theme
4. pencil_batch_get -> Read design tree
5. Map Pencil components to shadcn/ui
6. Generate code with semantic Tailwind classes
```

See [design-to-code-workflow.md](references/design-to-code-workflow.md) for complete workflow.

## Target Stack

- **Framework**: React/Next.js
- **Styling**: Tailwind CSS v4 (`@theme` blocks, not `tailwind.config.ts`)
- **Components**: shadcn/ui
- **Language**: TypeScript
- **Icons**: Lucide React
- **Utilities**: CVA (variants), `cn()` from `@/lib/utils`
- **Token Pipeline**: Style Dictionary + style-dictionary-utils (W3C DTCG)

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|-----------------|
| Creating a button from scratch | Search for existing button, insert as `ref` |
| Using `fill: "#3b82f6"` | Use variable reference `primary` |
| Using `cornerRadius: 8` | Use variable reference `radius-md` |
| Generating `bg-[#3b82f6]` | Use semantic class: `bg-primary` |
| Not checking for overflow | Call `pencil_snapshot_layout(problemsOnly: true)` after every section |
| Skipping screenshots | Call `pencil_get_screenshot` after every section |
| export succeeds but screenshots/ empty | Re-run `export_nodes`; verify directory contains files before marking task done |
| Generating a new logo | Copy existing logo with `C()` |
| Using `tailwind.config.ts` | Use CSS `@theme` block (Tailwind v4) |

## Resources

- [Pencil Docs](https://docs.pencil.dev)
- [Design as Code](https://docs.pencil.dev/core-concepts/design-as-code)
- [Variables](https://docs.pencil.dev/core-concepts/variables)
- [Components](https://docs.pencil.dev/core-concepts/components)
- [Design to Code](https://docs.pencil.dev/design-and-code/design-to-code)
