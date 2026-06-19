# Plan: User Profile Feature

## Task 1: Create profile endpoint

Implement `GET /api/profile` returning the authenticated user's profile as
`{ user_id, bio, avatar_url }` (`200`), or `{ error: "not_found" }` (`404`).

**File:** `src/profile.ts`

**Steps:**
- Register `GET /api/profile` on the Express router
- Read `userId` from `req.user` (set by the existing auth middleware)
- Fetch the profile row via `getProfileByUserId(userId)` (Task 2)
- Return `404 { error: "not_found" }` if absent, else `200` with `serializeProfile(row)` (Task 3)

## Task 2: Profile data model + repository

Add a `profiles` table (`user_id` FK → users.id, `bio` text, `avatar_url` text)
and a repository accessor.

**Files:** `src/db/schema.sql`, `src/profiles/repository.ts`

**Steps:**
- `CREATE TABLE profiles (...)` with `NOT NULL` on `user_id` and a btree index on `user_id`
- `getProfileByUserId(userId: string): Promise<ProfileRow | null>` — parameterized `SELECT user_id, bio, avatar_url FROM profiles WHERE user_id = $1`

## Task 3: Profile serialization

Map a DB row to the API JSON shape `{ user_id: string; bio: string; avatar_url: string }`.

**File:** `src/profiles/serializer.ts`

**Steps:**
- Define `serializeProfile(row: ProfileRow)` returning exactly `{ user_id, bio, avatar_url }`
- Map each field explicitly so future columns never leak into the response

## Task 4: Tests

**File:** `src/profile.test.ts`

**Steps:**
- `200` path: existing user returns `{ user_id, bio, avatar_url }`
- `404` path: missing profile returns `{ error: "not_found" }`
- `401` path: no `req.user` → unauthorized
