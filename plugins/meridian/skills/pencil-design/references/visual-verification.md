# Visual Verification

> Workflow step: **V2-2 / V2-4. Visual Verification**

Screenshot-based verification workflow to catch visual issues invisible in the node tree.

## Why This Matters

Layout and spacing issues are invisible in the node tree. Screenshots reveal:

- Misaligned elements that seem correct in the tree
- Spacing that is technically valid but visually unbalanced
- Text rendering differences (wrong font size, weight, contrast)
- Colors that look wrong together
- Missing content or empty areas
- Broken component instances

## Verification Workflow

### Section-by-Section Verification

Do NOT build an entire screen and then verify. Verify after each section:

```
Build header   -> Screenshot header   -> Fix issues
Build hero     -> Screenshot hero     -> Fix issues
Build features -> Screenshot features -> Fix issues
Build footer   -> Screenshot footer   -> Fix issues
Final          -> Screenshot full page -> Final review
```

### Step 1: Take a Screenshot

After completing a section:

```javascript
pencil_get_screenshot({
  filePath: "path/to/file.pen",
  nodeId: "sectionNodeId"
})
```

For the full screen at the end:

```javascript
pencil_get_screenshot({
  filePath: "path/to/file.pen",
  nodeId: "screenNodeId"
})
```

### Step 2: Analyze the Screenshot

**Alignment**

- Are elements properly centered or left/right aligned?
- Do columns have equal widths?
- Are grid items consistently spaced?

**Spacing**

- Is there adequate padding inside containers?
- Are gaps between elements consistent?
- Does spacing follow an 8px grid or the design system's spacing scale?

**Typography**

- Is text readable (sufficient size and contrast)?
- Are headings visually distinct from body text?
- Is any text cut off, overlapping, or overflowing?

**Color and Contrast**

- Do colors match the design system variables?
- Is there sufficient contrast for readability?
- Does the color scheme feel cohesive?

**Completeness**

- Are all expected elements present?
- Are icons/images placed correctly?
- Are there any empty or broken areas?

### Step 3: Check Layout Problems

Run in parallel with the screenshot:

```javascript
pencil_snapshot_layout({
  filePath: "path/to/file.pen",
  parentId: "sectionNodeId",
  maxDepth: 3,
  problemsOnly: true
})
```

Catches programmatic issues:
- Clipped elements (content extends beyond parent bounds)
- Overlapping siblings
- Elements positioned outside their parent

### Step 4: Fix and Re-verify

1. Fix each issue using `pencil_batch_design` with `U()` operations
2. Take a new screenshot to confirm the fix
3. Run `pencil_snapshot_layout` again to confirm no new issues

## When to Take Screenshots

| Moment | What to Screenshot |
|--------|--------------------|
| After building a section | The section's root frame |
| After fixing an issue | The affected area |
| When design is complete | The full screen/artboard |
| After modifying existing design | The changed section |
| After bulk property updates | At least one affected area |
| When comparing variants | Both variants side by side |

## Screenshot Retention and Promotion

Design iterations produce many intermediate screenshots. Committing every one of them bloats the repository with binary files and makes PR review meaningless. Follow this retention policy.

### Two-tier storage

```
docs/designs/<feature>/screenshots/
├── *.png                # Final approved screenshots (committed)
└── .tmp/                # Intermediate iteration screenshots (GITIGNORED)
```

- `docs/designs/**/screenshots/.tmp/` MUST be listed in `.gitignore`.
- Save every `pencil_get_screenshot` output to `.tmp/` first.
- Only **promote** a screenshot to `screenshots/` after the section has been approved by the user.

### Promotion workflow

1. Iterate in `.tmp/`:
   ```
   pencil_get_screenshot -> screenshots/.tmp/hero-v1.png
   pencil_get_screenshot -> screenshots/.tmp/hero-v2.png
   pencil_get_screenshot -> screenshots/.tmp/hero-v3.png
   ```
2. User approves `hero-v3.png`.
3. **Promote**: move `hero-v3.png` to `screenshots/hero.png` (drop the version suffix — final approved screenshots do not need versioning since git history provides it).
4. Delete everything else in `.tmp/` for this feature — it's already gitignored, but local cleanup keeps the working copy tidy.

### What gets a final screenshot

Only these artifacts deserve a committed screenshot in `screenshots/`:

- The final approved wireframe (from V2-2): `wireframe.png`
- One screenshot per key component variant (from V2-3): `<component>-<variant>.png`
- The final full-page design (from V2-4): `<screen>-desktop.png`, `<screen>-mobile.png`

Do NOT commit screenshots of intermediate iterations, exploration, or process snapshots.

### Naming convention

- Use lowercase, kebab-case: `alert-card-critical.png`, not `AlertCard_Critical.PNG`
- No version suffixes in committed filenames: `button.png`, not `button-v3-final.png`
- Breakpoint variants use suffix: `dashboard-mobile.png`, `dashboard-desktop.png`

## Common Issues Found Only Through Screenshots

| Issue | Symptom |
|-------|---------|
| Wrong font weight | Text looks too thin or too bold |
| Inconsistent padding | Some cards have more internal space |
| Color too similar to background | Element is hard to see |
| Alignment drift | Elements slightly off from each other |
| Missing gap | Two sections run directly into each other |
| Broken auto-layout | Children stack in unexpected direction |
| Icon too small/large | Icon disproportionate to adjacent text |
| Image aspect ratio wrong | Image appears stretched or squished |

## Full-Screen Final Review Checklist

- [ ] Does the overall visual hierarchy make sense?
- [ ] Are sections clearly separated?
- [ ] Is spacing consistent from top to bottom?
- [ ] Does it look professional and polished?
- [ ] On mobile: does everything fit within the 375px frame?
- [ ] Are there any empty gaps or broken areas?
- [ ] Does the color scheme work as a whole?
- [ ] Is there adequate white space?

## See Also

- [wireframe-and-layout.md](wireframe-and-layout.md) — Fix patterns for overflow issues
- [component-specification.md](component-specification.md) — Capturing component states
