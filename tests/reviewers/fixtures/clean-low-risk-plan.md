# Plan: Search Feature

## Prerequisites

- `CREATE INDEX idx_items_name ON items (name)` — prefix search needs the btree index
- `items.name` is `TEXT NOT NULL`

## Task 1: Search endpoint

Implement `GET /api/search?q=...` returning cursor-paginated prefix-match results.

**File:** `src/search.ts`

**Steps:**
- Validate `q`: non-empty, trimmed, max 100 chars; reject `400 { error: "invalid_query" }` otherwise
- Escape SQL wildcards in `q` (`%`, `_`) so user input cannot widen the LIKE match
- Run a prefix query that uses the index (no leading `%`): parameterized `SELECT id, name FROM items WHERE name LIKE $1 || '%' AND name > $2 ORDER BY name LIMIT 21` (21 so `has_more` is computable; bind `q` and `next_key`)
- Return `{ results: { id, name }[], has_more: boolean, next_key: string | null }` — no `total`, avoiding a second `COUNT` scan

## Task 2: Results page

Render `results` (HTML-escaped by React) with a "Load more" control driven by `next_key`.

**File:** `src/components/SearchResults.tsx`

## Tests

- `src/search.test.ts`:
  - empty query → `400`
  - wildcard `q=%` is escaped → returns only literal-prefix matches, never the whole table
  - results ordered by `name`; `next_key` returns the next page and then `has_more: false`
  - XSS attempt (`q=<script>`) is reflected safely (escaped)
