# Reviewer Behavioral Tests (B-layer)

Behavioral tests for Rune's reviewer prompts: **plant an obvious bug in a
synthetic diff, feed it to a reviewer prompt via `claude -p` (opus), and verify
the reviewer (a) flags the bug, (b) assigns Critical/High severity, (c) does
NOT approve** (sycophancy guard).

Contrast with the A-layer (`tests/hooks/`): A-layer is deterministic, zero-LLM,
runs in CI. B-layer runs a **real LLM** — each scenario costs ~$0.1-0.5 and is
non-deterministic.

## NOT in CI

Run manually — after editing a reviewer prompt, or before a release.

```bash
# all planted-bug scenarios
./tests/reviewers/run-all.sh

# one scenario
./tests/reviewers/run-reviewer-test.sh tests/reviewers/fixtures/sql-injection.diff \
  "sql injection|injection|注入|参数化|拼接" "Implement a user lookup."
```

## What it guards

The reviewer prompt's ability to catch obvious security bugs and refuse to
approve them. If a prompt edit makes the reviewer **miss a planted Critical
bug** or **rubber-stamp a bad diff** (sycophancy), this catches it.

## Scenarios

| Fixture | Reviewer | Planted bug |
|---------|----------|-------------|
| `sql-injection.diff` | code-quality (opus) | string-concatenated SQL |
| `plaintext-password.diff` | code-quality (opus) | plaintext password compare + logging the hash |
| `hardcoded-secret.diff` | code-quality (opus) | hardcoded API key |
| `spec-missing-requirement.diff` | spec (sonnet) | implementation missing required props/feature |
| `python-mutable-default.diff` | python (sonnet) | mutable default arg, no typing, `== None` |
| `ts-any.diff` | typescript (sonnet) | `any` props, missing useEffect deps, floating promise |
| `global-cross-task-conflict.diff` | global (opus) | cross-task type mismatch (User.id string vs Order.userId number) |
| `plan-with-defects.md` | plan (sonnet) | placeholders / TODO / vague tasks in a plan document |
| `plan-with-risks.md` | tech-risk (sonnet) | no tests / N+1 / no pagination in a plan document |

## How it works

`run-reviewer-test.sh` is a **generic reviewer runner**:
- env selects the prompt template (`PROMPT` + `PROMPT_SUBDIR`), model (`MODEL`),
  and per-reviewer conclusion vocabulary (`APPROVE_REGEX` / `BLOCK_REGEX` /
  `SEVERITY_REGEX` — spec concludes 合规/不合规 + 偏离类型; plan concludes
  Approved/Issues Found; tech-risk concludes Approved/Needs-Attention/Block).
- **prompt extraction** handles two template shapes: code-review/design are
  inline prose (used whole); writing-plans wrap the prompt in a ```Task-tool
  code block under `prompt: |` (extracted + dedented).
- the fixture can be a **diff** (code reviewers) OR a **plan document**
  (plan / tech-risk). The fixture rides in the user message; the role +
  checklist ride in the system prompt. Tools are disabled (no stray `npm audit`,
  no autonomous loop).

## Notes

- **Reviewer often replies in Chinese** — bug-keyword patterns include both
  English and Chinese terms. When adding a scenario, cover both.
- **Non-deterministic**: a rare flake (reviewer phrases a flag outside the
  keyword set) is possible. Re-run once before treating a failure as real.
- **Covered (7/8)**: `code-quality` (opus), `spec` / `python` / `typescript`
  (sonnet), `global` (opus), `plan-reviewer` / `technical-risk-reviewer`
  (sonnet). Only `design-review` remains — it reviews design artifacts (not
  diffs/plans) and needs filesystem Read, so it needs its own harness shape.
  Add a reviewer by writing a fixture that plants a bug **within its remit** +
  a run line in `run-all.sh`.
- **Bug must match the reviewer's remit**: language reviewers explicitly skip
  security (code-quality's job), so a SQL-injection bug against the
  python/typescript reviewer would wrongly "pass". Each scenario plants the bug
  its target reviewer is responsible for.
