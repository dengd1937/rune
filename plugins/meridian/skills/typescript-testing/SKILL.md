---
name: typescript-testing
description: TypeScript/React testing strategies using Vitest, React Testing Library, Playwright, MSW, and axe-core with TDD methodology.
origin: meridian
---

# TypeScript/React Testing Patterns

Comprehensive testing strategies for TypeScript/React applications using Vitest, React Testing Library, Playwright, MSW, and axe-core.

## When to Activate

- Writing new TypeScript/React code (follow TDD: red, green, refactor)
- Designing test suites for React components
- Reviewing TypeScript test coverage
- Setting up testing infrastructure (MSW, Playwright, axe-core)

---

## 1. Test-Driven Development

Always follow the TDD cycle:

1. **RED**: Write a failing test for the desired behavior
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve code while keeping tests green

Minimum coverage: **80%**

```bash
vitest run --coverage
```

---

## 2. Unit & Component Testing

Test user-visible behavior with React Testing Library, NOT implementation details.

```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { UserCard } from './UserCard'

describe('UserCard', () => {
  it('should call onSelect when clicked', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()

    render(<UserCard user={{ id: '1', name: 'Alice' }} onSelect={onSelect} />)

    await user.click(screen.getByRole('button'))
    expect(onSelect).toHaveBeenCalledWith('1')
  })
})
```

### Selector Priority

Use selectors in this order of preference:

1. `getByRole` - semantic roles (preferred)
2. `getByLabelText` - form elements
3. `getByText` - visible text
4. `getByTestId` - last resort

**NEVER** use CSS class names or DOM hierarchy as selectors.

---

## 3. Hooks Testing

```typescript
import { renderHook, act } from '@testing-library/react'
import { useCounter } from './useCounter'

it('should increment counter', () => {
  const { result } = renderHook(() => useCounter())

  act(() => result.current.increment())

  expect(result.current.count).toBe(1)
})
```

---

## 4. API Mocking with MSW

Intercept network requests with MSW instead of mocking fetch/axios implementations.

```typescript
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Alice' })
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

---

## 5. E2E Testing with Playwright

Use Playwright as the E2E testing framework for critical user flows.

```typescript
import { test, expect } from '@playwright/test'

test('user login flow', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Email').fill('user@example.com')
  await page.getByLabel('Password').fill('password')
  await page.getByRole('button', { name: 'Sign in' }).click()

  await expect(page).toHaveURL('/dashboard')
})
```

---

## 6. Visual Regression Testing

Use Playwright's built-in screenshot comparison to catch unintended visual changes.

```typescript
import { test, expect } from '@playwright/test'

test('dashboard visual regression', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveScreenshot('dashboard-full.png', {
    maxDiffPixelRatio: 0.01,
  })
})

test('alert card component states', async ({ page }) => {
  for (const variant of ['default', 'critical', 'warning']) {
    await page.goto(`/components/alert-card?variant=${variant}`)
    await expect(page.getByTestId('alert-card')).toHaveScreenshot(
      `alertcard-${variant}.png`,
      { maxDiffPixelRatio: 0.01 }
    )
  }
})
```

Baseline screenshots are committed to the repository. On failure, Playwright generates a diff image for review.

---

## 7. Accessibility Testing

Use **axe-core** via `@axe-core/playwright` for automated WCAG 2.1 AA compliance checks.

```typescript
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('dashboard accessibility', async ({ page }) => {
  await page.goto('/dashboard')
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze()
  expect(results.violations).toEqual([])
})
```

### Automated vs Manual Coverage

Automated checks cover:
- Color contrast
- ARIA attributes
- Semantic HTML
- Keyboard focus order
- Form labels

Manual review is still needed for:
- Keyboard navigation flow
- Screen reader announcements
- Focus trap in modals

### Dependencies

```bash
npm install --save-dev @axe-core/playwright
```

---

## 8. Test Organization

Group tests with `describe` by feature. Co-locate test files with source.

```
src/
├── components/
│   ├── UserCard.tsx
│   └── UserCard.test.tsx      # Component tests
├── hooks/
│   ├── useAuth.ts
│   └── useAuth.test.ts        # Hook tests
├── lib/
│   ├── api.ts
│   └── api.test.ts            # Utility tests
└── __mocks__/
    └── handlers.ts            # MSW handlers
```

---

## 9. Anti-Patterns

**NEVER:**

- **Test mock behavior instead of real functionality** - asserting what the mock returns proves nothing
- **Add test-only methods to production code** - tests must not intrude on production code
- **Use async assertions inside `.forEach`** - use `for...of` or `Promise.all` + `.map` instead
- **Replace behavioral assertions with snapshots** - snapshots capture structural changes, not functional correctness
- **Depend on test execution order** - each test must be independent with no shared side effects
- **Test framework internals** - never assert React state values directly or call internal component methods
