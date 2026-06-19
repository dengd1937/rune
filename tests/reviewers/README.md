# Reviewer Behavioral Tests (B-layer)

Behavioral tests for Rune's reviewer prompts, run via `claude -p` (real LLM).
Each reviewer is tested in **two directions** — recall × precision:

- **block** (planted bug): plant an obvious bug within the reviewer's remit,
  feed the diff/plan to the reviewer, and verify it (a) flags the bug, (b)
  signals severity, (c) **explicitly blocks** (positive assertion — a
  rubber-stamper that never blocks fails here).
- **approve** (clean control): feed the same context with the bug **fixed**, and
  verify the reviewer **approves and does not block**. A reviewer that
  over-blocks clean code fails here.

A prompt edit that makes a reviewer **miss a planted bug** (sycophancy) is caught
hard. A reviewer that **blocks clean code** (over-blocking) is surfaced as an
advisory signal — see Notes for why approve is soft, not a hard gate.

Contrast with the A-layer (`tests/hooks/`) and C-layer (`tests/skills/`): those
are deterministic, zero-LLM, run in CI. B-layer runs a **real LLM** — each
scenario costs ~$0.1-0.5 and is non-deterministic.

## NOT in CI

Run manually — after editing a reviewer prompt, or before a release.

```bash
# all scenarios (9 block + 7 approve)
./tests/reviewers/run-all.sh

# one scenario (defaults to block direction)
PROMPT=code-quality-reviewer-prompt.md MODEL=claude-opus-4-8 \
  ./tests/reviewers/run-reviewer-test.sh tests/reviewers/fixtures/sql-injection.diff \
  "sql injection|injection|注入|parameteriz|参数化|concat|拼接|unsanitiz"
```

## Scenarios

Each reviewer has a planted-bug fixture (block) and a clean counterpart (approve):

| Reviewer | block fixture (must flag + block) | approve fixture (must approve) |
|----------|-----------------------------------|--------------------------------|
| code-quality (opus) | `sql-injection.diff`, `plaintext-password.diff`, `hardcoded-secret.diff` | `clean-secure-auth.diff` |
| spec (sonnet) | `spec-missing-requirement.diff` | `clean-spec-compliant.diff` |
| python (sonnet) | `python-mutable-default.diff` | `clean-python.diff` |
| typescript (sonnet) | `ts-any.diff` | `clean-ts.diff` |
| global (opus) | `global-cross-task-conflict.diff` | `clean-cross-task.diff` |
| plan (sonnet) | `plan-with-defects.md` | `clean-plan.md` |
| tech-risk (sonnet) | `plan-with-risks.md` | `clean-low-risk-plan.md` |

Each clean fixture mirrors its buggy counterpart's context with the bug fixed —
a true control, not an unrelated clean file.

## How it works

`run-reviewer-test.sh` is a **generic reviewer runner** driven by env:
- `EXPECT=block` (default) | `approve` — selects the verdict direction.
- `PROMPT` + `PROMPT_SUBDIR` select the prompt template; `MODEL` selects opus/sonnet.
- `APPROVE_REGEX` / `BLOCK_REGEX` / `SEVERITY_REGEX` — per-reviewer conclusion
  vocabulary (defaults cover EN+ZH; plan/tech-risk override with their Status forms).
- **prompt extraction** segments code fences first (no cross-fence bridging),
  then extracts the Task-tool `prompt: |` wrapper if present (writing-plans);
  prose templates (code-review/design) are used whole. A leftover-placeholder
  warning fires if a template grew a new `{{VAR}}`/`[VAR_PATH]` the runner does
  not substitute.
- the fixture rides in the **user message**; the role + checklist ride in the
  **system prompt**. Tools are disabled.
- **the verdict is scoped to the conclusion** (text after the last `结论` /
  `Status:` marker): the approve/block check looks there, so body reasoning like
  "no SQL injection" / "no must-fix issues" isn't misread as a block. Recall
  (bug keyword + severity) still scans the full output, since the bug discussion
  lives in the body.

## Notes

- **Reviewer often replies in Chinese** — keyword/conclusion patterns include
  both English and Chinese terms.
- **Non-deterministic**: a rare flake (reviewer phrases a flag outside the
  pattern set) is possible. Re-run once before treating a failure as real.
- **Covered (7/8 reviewers)**: code-quality / spec / python / typescript /
  global / plan / tech-risk, each in **both directions**. Only `design-review`
  remains — it reviews design artifacts (not diffs/plans) and needs filesystem
  Read, so it needs its own harness shape.
- **Bug must match the reviewer's remit**: language reviewers skip security
  (code-quality's job), so a SQL-injection bug against the python/typescript
  reviewer would wrongly "pass". Each block scenario plants the bug its target
  reviewer is responsible for; each approve scenario is clean for that remit.
- **The approve direction is the precision guard** — the dual of the sycophancy
  guard. Without it, a reviewer that blocks everything would pass every block
  scenario; the approve scenarios catch that.
- **The approve (precision) direction is a SOFT signal, not a hard gate.** Every
  strict reviewer (HIGH=block by design, "宁严勿宽") non-deterministically invents
  pedantic nits as HIGH on genuinely-clean code — e.g. flagging a `for`+`append`
  loop as "non-Pythonic," or a typed `fetch().json()` as an "unnecessary type
  assertion," or a missing JSDoc. So a single approve run can flake (the same
  clean fixture passes one run and fails the next). `run-all.sh` therefore treats
  approve failures as **advisory** (counted, non-fatal) and only hard-fails on
  **block (recall)** failures, which are reliable — planted bugs are unambiguous.
  Read approve results across multiple runs: **consistent** fails indicate genuine
  over-strictness (observed: code-quality inflates route-level concerns like
  rate-limiting to HIGH on function-scoped diffs; tech-risk is adversarial by
  design). Block-mode sycophancy (a reviewer that never blocks a planted bug)
  remains a hard, reliable failure.
