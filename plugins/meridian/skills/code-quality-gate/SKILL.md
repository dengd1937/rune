---
name: code-quality-gate
description: Run quality checks after editing files — format, typecheck, and console.log detection. Use after writing or modifying source files before moving to the next task.
origin: ECC
---

# Code Quality Gate

Run this skill after editing source files to catch formatting issues, type errors, and debug artifacts before they accumulate.

## When to Activate

- After writing or modifying source files in a response
- Before switching to a new task or file
- Before committing changes
- When a code review agent flags quality issues

## Checks to Perform

### 1. Format

Auto-format all modified files using the project's configured formatter.

**JavaScript / TypeScript**
```bash
# Biome (preferred if biome.json exists)
npx biome format --write <files>

# Prettier (fallback)
npx prettier --write <files>
```

**Python**
```bash
# Ruff (preferred)
ruff format <files>

# Black (fallback)
black <files>
```

**Go**
```bash
gofmt -w <files>
```

### 2. Lint

Run the linter on modified files and fix auto-fixable issues.

**JavaScript / TypeScript**
```bash
# Biome
npx biome lint --write <files>

# ESLint
npx eslint --fix <files>
```

**Python**
```bash
ruff check --fix <files>
```

**Go**
```bash
golangci-lint run <files>
```

### 3. Typecheck

Run the type checker across the project (not just modified files, since changes can affect other modules).

**TypeScript**
```bash
npx tsc --noEmit
```

**Python (mypy)**
```bash
mypy <module_or_path>
```

### 4. Console / Debug Artifact Detection

Scan modified files for debug statements that should not be committed.

**Patterns to detect:**
- `console.log(`, `console.debug(`, `console.warn(` (JS/TS)
- `print(`, `pprint(`, `breakpoint()` (Python, unless in test files)
- `debugger;` (JS/TS)
- `TODO:`, `FIXME:`, `HACK:` (flag only, do not block)

**Action:** Remove or replace with proper logging before proceeding.

## Pass Criteria

All checks must pass before the quality gate is considered satisfied:

| Check | Pass Condition |
|---|---|
| Format | No formatting changes remain after auto-fix |
| Lint | Zero errors (warnings allowed) |
| Typecheck | Zero type errors |
| Debug artifacts | No `console.log` / `debugger` / `breakpoint()` in non-test files |

## Failure Handling

- **Format/lint failures**: Fix automatically where possible, then re-run to verify.
- **Type errors**: Fix the root cause in the source file — do not suppress with `@ts-ignore` or `type: ignore` unless absolutely necessary and commented.
- **Debug artifacts found**: Remove them. If the output is intentional, replace with a proper logger (`logger.debug(...)`, `logging.debug(...)`, etc.).
- **Config file changes blocked**: Do not loosen linter or formatter rules to make checks pass. Fix the code instead.

## Scope

Run checks only on files modified in the current response or task. Do not run full-project linting unless the task explicitly requires it, to keep feedback fast.
