# L1 Lightweight UI Change

Use `L1` when **all** of the following are true:

- No new page or major layout pattern
- No new interaction model
- No new design-system component
- No new token is required

## Actions

1. Confirm the change is local and does not introduce new design primitives.
2. **If `DESIGN.md` exists**, verify the proposed change complies with its *Do's and don'ts* and stays within defined color/typography/component style boundaries. If the change reveals a design identity gap, record it and ask for user decision instead of inventing a new visual rule.
3. Capture before/after screenshots for the affected area.
4. Pass the design note data to → doc-ops skill（write 模式，模板：`l1-design-note`）
   - what changed
   - why it changed
   - which existing tokens/components were reused
5. Proceed directly to `writing-plans` → `subagent-driven-development`.

## Outputs

- Updated screenshot(s) for the affected surface
- A short design note in `intent.md` or the PR

## Escalation Rule

If the change grows into a new page, new interaction, or new token, upgrade immediately to `L2` (full design-workflow skill V2-1 to V2-5).
