---
name: design-workflow
description: "Use after brainstorm for tasks involving UI — new pages, new components, new visual interactions, or new design tokens. TRIGGER when: new UI feature, new page, new component, or visual change; tasks involving docs/designs/ directories, *.pen files, Pencil MCP tools, or design tokens. Skip for: backend-only, config-only, refactoring without visual impact. Terminal state: handoff to writing-plans skill."
metadata:
  author: sre-copilot
  version: "2.0"
---

# Design Workflow v2

> Orchestrates UI design work using Pencil MCP and Style Dictionary.
> Execution-layer Pencil operations are delegated to the **pencil-design** skill.

## Prerequisites

- Pencil MCP server running locally (desktop client or IDE extension)
- [pencil-design skill](../pencil-design/SKILL.md) installed
- `style-dictionary` and `style-dictionary-utils` available for the token pipeline
- (Optional) `DESIGN.md` in the project root — if present, it becomes the visual identity SSOT

---

## Core Rules

1. **Route UI work up front.**
   - Small UI tweaks go through `L1` — see [l1-lightweight.md](references/l1-lightweight.md).
   - New pages, new components, new interactions, or new tokens go through `L2`.
2. **Only three design gates exist in the standard path.**
   - `Gate 1`: direction confirmation
   - `Gate 2`: layout confirmation
   - `Gate 3`: final approval before handoff
3. **Tokens remain the source of truth.**
   - Do not hardcode visual values.
   - Do not edit generated token files by hand.
4. **Design docs capture constraints, not duplicate implementation.**
   - Markdown component docs describe behavior, mapping, responsive rules, accessibility, and visual constraints.
   - Source code owns the final TypeScript props and implementation details.
5. **DESIGN.md is the visual identity authority when it exists.**
   - Read `DESIGN.md` at the start of every V2 stage.
   - Tokens are derived from DESIGN.md (color palette → brand tokens, typography → font tokens, etc.).
   - The workflow never silently writes back to DESIGN.md. If a design need falls outside DESIGN.md scope, record a design identity gap and ask the user whether to constrain the design or intentionally update DESIGN.md.

---

## DESIGN.md Integration

When `DESIGN.md` exists in the project root, it serves as the visual identity single source of truth (SSOT). The 9 DESIGN.md sections map to three roles:

- **Token derivation** (6 sections): Color palette → color tokens; Typography → font tokens; Layout principles → spacing/radius/breakpoint tokens; Depth and elevation → shadow tokens; Component styles → component-level token defaults; Responsive behavior → breakpoint tokens and touch targets.
- **Validation constraint** (1 section): Do's and don'ts — applied as hard validation rules during V2-3 and V2-4.
- **Context reference** (2 sections): Visual theme and atmosphere, Agent prompt guide — used as ambient context, not tokenized.

See pencil-design skill `tokens-and-variables.md` for the complete mapping table.

Before treating DESIGN.md as authoritative, run the DESIGN.md preflight in [design-md-preflight.md](references/design-md-preflight.md). Incomplete DESIGN.md files can still guide the workflow, but missing sections become explicit gaps instead of hidden assumptions.

---

## Directory Layout

All design artifacts live under `docs/designs/<feature>/`. See pencil-design skill for full directory structure and file naming conventions.

**Git rules:**

- Add `docs/designs/**/screenshots/.tmp/` to `.gitignore`.
- Only promote screenshots from `.tmp/` to `screenshots/` after approval.
- `intent.md` is long-term knowledge. Keep it for the life of the feature.
- **`.pen` files live in the Pencil editor (like Figma cloud). They are NOT committed to `docs/designs/`.** During design and development, use Pencil MCP to read/write the active design directly. Screenshots, tokens, source maps, and component contracts are the persistent artifacts in the repo.
- Commit tokens, token source maps, components, screenshots; `.tmp/` is gitignored.

---

## L2 Standard Workflow

### V2-1. Design Intent

Investigate requirements and establish design direction before editing the canvas.

**前序产物验证：** 读取 brainstorm 的 capability mapping，确定本 feature 触及的 capability spec（`docs/specs/<capability>-spec.md`）。capability spec 不存在 → 报告用户，不继续。

```
capability specs = docs/specs/<capability>-spec.md（brainstorm mapping 指明）
designs          = docs/designs/{feature}/
```

后续所有 V2 阶段用 `feature` 名称定位 `docs/designs/{feature}/`；行为需求从相关 capability specs 读。

**Actions:**

- **If `DESIGN.md` exists**, read it first and run DESIGN.md preflight: complete sections become visual identity constraints; missing or ambiguous sections become design identity gaps that require user decision before they are treated as defaults
- **Read the relevant capability spec(s)** (`docs/specs/<capability>-spec.md`) as the functional requirements input: UI scope, user flows, behavior scenarios, and design constraints come from the brainstorm stage. Behavior truth lives in capability specs; product framing / competitor analysis are conversation-level context, not durable docs.
- Analyze the UI scope: pages, components, interactions, and constraints
- **If `DESIGN.md` exists**, classify components into "matches existing DESIGN.md component styles", "requires documented identity gap", or "requires user-approved DESIGN.md update"
- Search the project for reusable design assets and existing `docs/designs/` directories
- Use `pencil_batch_get` with `patterns: [{ reusable: true }]` to discover reusable components
- Use `pencil_get_variables` to inspect the existing token system
- Pass the design intent data to → doc-ops skill（write 模式，模板：`design-intent`

**Output:** `docs/designs/<feature>/intent.md`（通过 doc-ops write 写入）

**Gate 1:** User confirms the design direction.

---

### V2-2. Wireframe + Baseline Tokens

Create the page structure and establish the minimum token set needed to support it.

**Actions:**

1. **If `DESIGN.md` exists**, derive baseline tokens from it (see mapping table in pencil-design `tokens-and-variables.md`):
   - Color tokens ← DESIGN.md *Color palette and roles*
   - Typography tokens ← DESIGN.md *Typography rules*
   - Spacing / border-radius tokens ← DESIGN.md *Layout principles*
   - Shadow tokens ← DESIGN.md *Depth and elevation*
   - Component skeleton styles ← DESIGN.md *Component styles*
   - *Visual theme and atmosphere* and *Agent prompt guide* sections serve as context reference only
   - *Do's and don'ts* is not tokenized — it applies as a validation constraint in V2-3 and V2-4
2. If `DESIGN.md` does not exist, define/confirm baseline tokens (brand, semantic, surface, typography, radius) as usual — see pencil-design skill for complete token reference.
3. Verify tokens with `pencil_get_variables`.
4. Pass token provenance data to → doc-ops skill（write 模式，模板：`token-source-map` when tokens are derived from DESIGN.md, existing variables, or fallback defaults.
5. Build the wireframe and page regions using reusable components and tokenized values only.
6. Capture review screenshots to `screenshots/.tmp/`.
7. Run `pencil_snapshot_layout({ problemsOnly: true })` on the affected screens.
8. Iterate until the page structure and regions are stable.

**Outputs:**

- Final approved wireframe screenshot(s) in `docs/designs/<feature>/screenshots/`
- `docs/designs/<feature>/tokens/source-map.md` when tokens are derived or updated

**Gate 2:** User confirms layout, page regions, and overall structure.

---

### V2-3. High-Fidelity Design + Token Expansion + Key Component Contracts

Refine the wireframe into the final design, expand the token system, and document only the component constraints that development genuinely needs.

**Actions:**

1. Refine the design to high fidelity in the active Pencil design.
2. **If `DESIGN.md` exists**, enforce its rules as hard guardrails:
   - Component styles must stay within DESIGN.md *Component styles* definitions
   - Colors must stay within DESIGN.md *Color palette and roles* scope
   - DESIGN.md *Do's and don'ts* are non-negotiable constraints
   - Responsive behavior must follow DESIGN.md *Responsive behavior* module
   - Any design element outside DESIGN.md scope must be flagged as a design identity gap; do not silently modify DESIGN.md or invent a new visual direction
3. Expand tokens (spacing, shadows, breakpoints, theme variants) as needed.
4. Update token source-map when tokens are added or their source changes.
5. Run token pipeline — see pencil-design skill.
6. Verify generated outputs (`tokens.css`, `tokens.ts`, `tailwind-preset.ts`).
7. Capture final component and screen screenshots to `screenshots/.tmp/`, then promote approved results.
8. Pass component contract data to → doc-ops skill（write 模式，模板：`component-contract`（doc-ops templates/component-contract.md 含完整模板：Variants、States、Responsive、Accessibility、Implementation Mapping、Design Constraints）

**Rule:** Do not duplicate full TypeScript props interfaces in markdown unless design decisions directly constrain the public API. Source code remains the authority for props.

**Completion standard:** Key components are covered, generated token outputs are consistent with `w3c.json`, and token provenance is current in `tokens/source-map.md`.

---

### V2-4. Design Review [hard gate]

Review all design artifacts before handoff. This is the single hard approval gate in the standard path.

> Playwright visual regression and axe-core accessibility audits belong to `subagent-driven-development` Step 1 (implementer subagent). This stage reviews design-time artifacts only.

**Phase 1 - Design-time visual checks**

1. Capture final screenshots for each documented breakpoint.
2. Run `pencil_snapshot_layout({ problemsOnly: true })` on relevant screens.
3. Pass layout report data to → doc-ops skill（write 模式，模板：`layout-report`
   - approved screenshots → `docs/designs/<feature>/screenshots/`

**Phase 2 - design-review skill**

调用 design-review skill 审查 `docs/designs/<feature>/`。该 skill 检查 token coverage, contract completeness, artifact consistency, a11y docs, responsive coverage, and DESIGN.md compliance when DESIGN.md exists.

**If `DESIGN.md` exists**, the agent additionally checks:
- Do all tokens trace back to a DESIGN.md rule?
- Are there colors, fonts, or component variants not defined in DESIGN.md?
- Does the design violate any DESIGN.md *Do's and don'ts*?
- Violations block handoff until resolved by either constraining the design or a user-approved DESIGN.md update.

**Visual quality is still reviewed by humans, not the agent.**

**Phase 3 - User approval**

1. Review the artifact report in conversation.
2. Present final screenshots and review findings.
3. On approval, pass verdict data to → doc-ops skill（write 模式，模板：`review-verdict`

**Outputs:**

- `docs/designs/<feature>/screenshots/layout-report.md`
- `docs/designs/<feature>/review-verdict.md`
- Design review report in conversation

**Gate 3:** User explicitly approves. Only then does the workflow hand off to development.

---

### V2-5. Handoff to Development Workflow

After Gate 3, design artifacts become inputs to the `writing-plans` skill, which produces the plan consumed by `subagent-driven-development`.

**同步设计产物到 FEATURE-CATALOG**（handoff 前必做）：调 doc-ops skill（sync 模式，scope 限定本 feature）：

- 该 feature 的 `Design Status` → `Done`
- 扫描 `docs/designs/<feature>/components/*.md`，写入 FEATURE-CATALOG 的 **Components 段**（Component | Feature | Base Component | Status）

**If `DESIGN.md` exists**, all handoff artifacts already comply with it (enforced in V2-3 and V2-4). Ensure `intent.md` references DESIGN.md as the visual authority so `writing-plans` and `subagent-driven-development` maintain the same constraints.

| Skill | Consumes | How |
|----------|----------|-----|
| writing-plans (plan creation) | `components/*.md`, `review-verdict.md`, `tokens/source-map.md` | Reference component contracts, DESIGN.md gaps, token provenance, and review findings in the implementation plan |
| subagent-driven-development (implementation) | `tokens/*`, `components/*.md`, `DESIGN.md` if present | Validate token usage, prevent hardcoded visual values, run Playwright visual regression, run axe-core accessibility audit |

**Implementation-side rule:** If implementation changes the visual contract or reveals a missing token, update `docs/designs/<feature>/` in the same PR. Do not patch around the gap with hardcoded values.

---

## Iteration Loops

- **L1 → L2**: scope expands to new page/component/token → upgrade immediately
- **Missing token**: add in Pencil → re-run pipeline → never edit generated files by hand
- **Review findings (V2-4 → V2-3)**: update design/screenshots/contracts → re-run V2-4
- **Dev discovers gap**: update design artifact in same PR → keep code and design aligned
- **Direction change**: update intent.md with new rationale → restart from V2-1
- **DESIGN.md violation found during V2-3 or V2-4**: constrain the design by default; if the visual identity itself must change, stop and request explicit user approval before DESIGN.md is updated

---

## Version Control Strategy

`.pen` files live in the Pencil editor and are NOT committed to the repo.

- Screenshots, tokens, and component contracts are the version-controlled artifacts
- Do not edit the same design in Pencil on multiple branches simultaneously
- Use Pencil MCP during development to read precise design properties

---

## shadcn/ui Fallback Priority

When the mapping table in pencil-design does not cover a component:

1. `shadcn/ui` official
2. `shadcn/ui` registry
3. `tremor`, `magicui`, `aceternity-ui`
4. Radix UI primitives
5. Handrolled component as the last resort

Do not jump straight to handrolled components.
