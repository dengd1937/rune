# Wireframe and Layout

> Workflow step: **V2-2. Wireframe + Baseline Tokens**

Covers component discovery, layout construction, and overflow prevention for building wireframes on the Pencil canvas.

## Component Discovery

### List All Reusable Components

Always do this at the start of any design task:

```javascript
pencil_batch_get({
  filePath: "path/to/file.pen",
  patterns: [{ reusable: true }],
  readDepth: 2,
  searchDepth: 3
})
```

Returns all components with their children. Example:

```json
{
  "id": "btn-primary",
  "name": "Button",
  "type": "frame",
  "reusable": true,
  "children": [
    { "id": "btn-label", "type": "text", "content": "Button" }
  ]
}
```

### Insert as a Ref Instance

```javascript
btn = I("parentFrameId", { type: "ref", ref: "btn-primary", width: "fill_container" })
```

### Customize the Instance

```javascript
U(btn + "/btn-label", { content: "Submit" })
```

### Replace Slots

```javascript
newContent = R(btn + "/content-slot", { type: "text", content: "Custom Content" })
```

### When to Create New

Only create from scratch when:

1. No similar component exists after checking `reusable: true`
2. The existing component is fundamentally different (not just a color/text change)
3. Building a new design system from an empty file

### Common Components to Search For

| Need | Search for names containing |
|------|----------------------------|
| Button | button, btn, cta |
| Text input | input, field, text-field |
| Card | card, tile, panel |
| Navigation | nav, navbar, sidebar, menu |
| Header | header, topbar, appbar |
| Footer | footer, bottom-bar |
| Modal/Dialog | modal, dialog, sheet |
| Badge/Tag | badge, tag, chip, label |
| Avatar | avatar, profile-pic |
| Table row | row, table-row, list-item |

## Layout Construction

### Auto-Layout

Use auto-layout instead of absolute positioning:

```javascript
// Vertical stack
U("parentId", { layout: "vertical", gap: 12 })

// Horizontal row
U("parentId", { layout: "horizontal", gap: 8 })
```

### Fill Container

Children should fill parent width in auto-layout frames:

```javascript
child = I(parent, { type: "frame", width: "fill_container", layout: "vertical" })
```

### Padding and Gap

```javascript
// Container padding
U("parentId", { padding: 16 })
// Per-side padding
U("parentId", { paddingLeft: 16, paddingRight: 16, paddingTop: 8, paddingBottom: 8 })
// Gap between children
U("parentId", { gap: 12 })
```

## Overflow Prevention

### For Text Elements

1. Always set text width to `fill_container`:

```javascript
text = I(container, { type: "text", content: "Long text...", width: "fill_container" })
```

2. Use `maxLines` for truncation:

```javascript
U("titleTextId", { maxLines: 1, width: "fill_container" })
```

### For Container Frames

1. Use auto-layout on parent frames
2. Set children to `width: "fill_container"`
3. Add padding to prevent content touching edges
4. Use `gap` for spacing between children

### For Mobile Screens (375-393px)

1. Screen frame: exact target width (e.g., 375px)
2. All direct children: `width: "fill_container"` with 16-20px horizontal padding
3. Text: always `width: "fill_container"`, never fixed width wider than ~335px
4. Images: constrain to container width

### Detection

After inserting content, always check:

```javascript
pencil_snapshot_layout({
  filePath: "path/to/file.pen",
  parentId: "screenId",
  maxDepth: 3,
  problemsOnly: true
})
```

### Fix Patterns

| Problem | Fix |
|---------|-----|
| Text clipped horizontally | Set text `width: "fill_container"` or reduce font size |
| Text clipped vertically | Increase parent height or set `maxLines` |
| Child wider than parent | Set child `width: "fill_container"` |
| Children overlapping | Add `layout: "vertical"` or `layout: "horizontal"` to parent |
| Content outside artboard | Reduce widths/padding, check descendants fit |

## Checklist

After every section:

- [ ] Called `pencil_batch_get` with `{ reusable: true }` to list components?
- [ ] Inserting components as `ref` instances (not recreating structure)?
- [ ] Customizing instances via `U()` on descendant paths?
- [ ] All text elements using `width: "fill_container"`?
- [ ] Mobile screens have 16-20px padding?
- [ ] Called `pencil_snapshot_layout` with `problemsOnly: true`?
- [ ] Called `pencil_get_screenshot` for visual verification?

## See Also

- [visual-verification.md](visual-verification.md) — Screenshot verification workflow
- [tokens-and-variables.md](tokens-and-variables.md) — Use variables for all style values
- [responsive-breakpoints.md](responsive-breakpoints.md) — Multi-artboard layout patterns
