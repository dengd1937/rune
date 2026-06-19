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

## How it works

`run-reviewer-test.sh` is a **generic reviewer runner**: env selects the prompt
template (`PROMPT`), model (`MODEL`), and per-reviewer conclusion vocabulary
(`APPROVE_REGEX` / `BLOCK_REGEX` / `SEVERITY_REGEX` — the spec reviewer
concludes 合规/不合规 and uses 偏离类型 rather than APPROVE/BLOCK and
CRITICAL/HIGH). It substitutes all placeholders, feeds **role + checklist** as
the system prompt and the **diff** as the user message to `claude -p`, then
greps the verdict. Tools are disabled (the reviewer only analyzes the diff — no
stray `npm audit`, no autonomous loop).

## Notes

- **Reviewer often replies in Chinese** — bug-keyword patterns include both
  English and Chinese terms. When adding a scenario, cover both.
- **Non-deterministic**: a rare flake (reviewer phrases a flag outside the
  keyword set) is possible. Re-run once before treating a failure as real.
- **Covered**: `code-quality` (opus, security), `spec` (sonnet, spec deviation),
  `python` / `typescript` (sonnet, language anti-patterns). `global-reviewer`
  and `design-review` are not yet covered (different fixture shapes). Add a
  reviewer by writing a fixture that plants a bug **within its remit** + a run
  line in `run-all.sh`.
- **Bug must match the reviewer's remit**: language reviewers explicitly skip
  security (code-quality's job), so a SQL-injection bug against the
  python/typescript reviewer would wrongly "pass". Each scenario plants the bug
  its target reviewer is responsible for.
