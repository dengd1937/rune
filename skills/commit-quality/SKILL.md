---
name: commit-quality
description: Pre-commit quality gate — validate commit message format, lint staged files, and scan for secrets and debug artifacts. Use before every git commit.
origin: ECC
---

# Commit Quality Gate

Run this skill before every `git commit` to enforce commit message conventions, catch last-minute quality issues, and prevent secrets from leaking into the repository.

## When to Activate

- Before running `git commit`
- After staging files with `git add`
- When the tdd-workflow or git-workflow skill reaches the commit step

## Checks to Perform

### 1. Commit Message Format

Validate that the commit message follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Allowed types:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`, `revert`

**Rules:**
- Subject line ≤ 72 characters
- Subject in imperative mood ("add feature", not "added feature")
- No period at end of subject
- Body and footer separated by blank lines

**Good examples:**
```
feat(auth): add OAuth2 login
fix(api): handle null response in user endpoint
test(auth): add unit tests for token validation
```

**Bad examples:**
```
fixed stuff          # no type, vague
Update.              # no type, period at end
feat: Added the new payment flow and also fixed the login bug and updated docs   # too long, too many concerns
```

### 2. Lint Staged Files

Run the linter on staged files only before committing.

**JavaScript / TypeScript**
```bash
# lint-staged (if configured)
npx lint-staged

# Manual: Biome
git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|js|jsx)$' | xargs npx biome lint

# Manual: ESLint
git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|js|jsx)$' | xargs npx eslint
```

**Python**
```bash
git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | xargs ruff check
```

### 3. Debug Artifact Scan

Check staged files for debug statements.

```bash
# Detect console.log / debugger in staged JS/TS files
git diff --cached | grep -E '^\+.*(console\.(log|debug|warn)|debugger)'

# Detect print / breakpoint in staged Python files
git diff --cached | grep -E '^\+.*(^print\(|breakpoint\(\))'
```

If found: remove before committing, or replace with a proper logger.

### 4. Secrets Scan

Check staged files for common secret patterns. Do not commit if any are found.

**Patterns to detect:**
- Hardcoded API keys: `api_key\s*=\s*["'][A-Za-z0-9]{20,}["']`
- Tokens: `(token|secret|password)\s*=\s*["'][^"']{8,}["']`
- AWS credentials: `AKIA[0-9A-Z]{16}`
- Private keys: `-----BEGIN (RSA |EC )?PRIVATE KEY-----`
- Connection strings with credentials: `://[^:]+:[^@]+@`

```bash
# Quick scan of staged diff
git diff --cached | grep -iE '(api_key|secret|password|token)\s*=\s*["\x27][^"\x27]{8,}'
```

If found: **stop immediately**, remove the secret, add the file to `.gitignore` if needed, and rotate the exposed credential.

### 5. No Hook Bypass

Never use flags that skip git hooks:

```
# NEVER use these
git commit --no-verify
git commit -n
git push --no-verify
```

These flags disable pre-commit, commit-msg, and pre-push hooks that protect the repository. If a hook is failing, fix the underlying issue instead of bypassing it.

## Pass Criteria

All checks must pass before committing:

| Check | Pass Condition |
|---|---|
| Commit message | Follows Conventional Commits format |
| Lint | Zero errors on staged files |
| Debug artifacts | None in staged files |
| Secrets | None in staged diff |
| Hook bypass | No `--no-verify` flag used |

## Failure Handling

- **Bad commit message**: Rewrite the message to follow the format above.
- **Lint errors**: Fix the errors in staged files, re-stage with `git add`, then retry.
- **Debug artifacts**: Remove `console.log` / `debugger` / `print()` statements, re-stage.
- **Secret detected**: Remove the secret immediately. Do not commit. Add to `.gitignore`. Rotate the credential if it was ever pushed.
- **Hook failure**: Investigate and fix the root cause. Never use `--no-verify` to bypass.
