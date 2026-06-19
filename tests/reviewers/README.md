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

| Fixture | Planted bug | Expected flag |
|---------|-------------|---------------|
| `sql-injection.diff` | string-concatenated SQL | SQL injection, Critical |
| `plaintext-password.diff` | plaintext password compare + logging the hash | plaintext/bcrypt, Critical |
| `hardcoded-secret.diff` | hardcoded API key | hardcoded secret/env var, Critical |

## How it works

`run-reviewer-test.sh` substitutes the placeholders in
`skills/code-review/code-quality-reviewer-prompt.md`, feeds the **role +
checklist** as the system prompt and the **diff** as the user message to
`claude -p --model opus`, then greps the verdict. Tools are disabled (the
reviewer only analyzes the diff — no stray `npm audit`, no autonomous loop).

## Notes

- **Reviewer often replies in Chinese** — bug-keyword patterns include both
  English and Chinese terms. When adding a scenario, cover both.
- **Non-deterministic**: a rare flake (reviewer phrases a flag outside the
  keyword set) is possible. Re-run once before treating a failure as real.
- Only `code-quality-reviewer-prompt.md` is covered (most-used, includes the
  OWASP security checklist). Extend to `spec-reviewer` / `design-review` etc.
  by adding fixtures + a run line in `run-all.sh`.
