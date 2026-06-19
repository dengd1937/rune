# Plan: Search Feature

## Task 1: Search endpoint

Implement the search endpoint.

**File:** `src/search.ts`

**Steps:**
- For each search request, run: `SELECT * FROM items WHERE name LIKE '%query%'`
- Return all matching results to the client
- No pagination for now (we can add it later)

## Task 2: Results page

Render all search results in a list.

Tests will be added after launch.
