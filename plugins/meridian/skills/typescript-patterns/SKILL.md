---
name: typescript-patterns
description: TypeScript/React patterns, shadcn/ui conventions, Tailwind v4 usage, and best practices for building robust frontend applications.
origin: meridian
---

# TypeScript/React Development Patterns

TypeScript, React, shadcn/ui, and Tailwind v4 patterns and best practices for building robust frontend applications.

## When to Activate

- Writing new TypeScript/React code
- Reviewing TypeScript/React code
- Refactoring existing frontend components
- Designing component APIs and props interfaces
- Setting up Tailwind or shadcn/ui patterns

---

## 1. Types and Interfaces

### Public API Types

Add parameter and return types to exported functions, shared utilities, and public class methods. Let TypeScript infer obvious local variable types.

```typescript
// Good: Explicit types on public APIs
interface User {
  firstName: string
  lastName: string
}

export function formatUser(user: User): string {
  return `${user.firstName} ${user.lastName}`
}
```

### Interfaces vs. Type Aliases

- Use `interface` for object shapes that may be extended or implemented
- Use `type` for unions, intersections, tuples, mapped types, and utility types
- Prefer string literal unions over `enum`

```typescript
interface User {
  id: string
  email: string
}

type UserRole = 'admin' | 'member'
type UserWithRole = User & {
  role: UserRole
}
```

### Avoid `any`

Use `unknown` for external or untrusted input, then narrow safely.

```typescript
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  return 'Unexpected error'
}
```

### React Props

Define component props with a named `interface` or `type`. Do not use `React.FC`.

```typescript
interface User {
  id: string
  email: string
}

interface UserCardProps {
  user: User
  onSelect: (id: string) => void
}

function UserCard({ user, onSelect }: UserCardProps) {
  return <button onClick={() => onSelect(user.id)}>{user.email}</button>
}
```

### JSDoc in JavaScript Files

In `.js` and `.jsx` files, use JSDoc when types improve clarity and a TypeScript migration is not practical.

```javascript
/**
 * @param {{ firstName: string, lastName: string }} user
 * @returns {string}
 */
export function formatUser(user) {
  return `${user.firstName} ${user.lastName}`
}
```

---

## 2. Immutability

Use spread operator for immutable updates. Never mutate existing objects.

```typescript
interface User {
  id: string
  name: string
}

function updateUser(user: Readonly<User>, name: string): User {
  return {
    ...user,
    name
  }
}
```

---

## 3. Error Handling

Use async/await with try-catch and narrow unknown errors safely.

```typescript
interface User {
  id: string
  email: string
}

declare function riskyOperation(userId: string): Promise<User>

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  return 'Unexpected error'
}

const logger = {
  error: (message: string, error: unknown) => {
    // Replace with your production logger (e.g., pino or winston).
  }
}

async function loadUser(userId: string): Promise<User> {
  try {
    const result = await riskyOperation(userId)
    return result
  } catch (error: unknown) {
    logger.error('Operation failed', error)
    throw new Error(getErrorMessage(error))
  }
}
```

---

## 4. Input Validation

Use Zod for schema-based validation and infer types from the schema.

```typescript
import { z } from 'zod'

const userSchema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
})

type UserInput = z.infer<typeof userSchema>

const validated: UserInput = userSchema.parse(input)
```

---

## 5. Tailwind CSS v4

### Semantic Classes Only

NEVER use arbitrary values. Always use semantic Tailwind utilities that map to design tokens.

```typescript
// BAD: Arbitrary values bypass the design system
<div className="bg-[#3b82f6] rounded-[6px] p-[24px] text-[14px]">

// GOOD: Semantic classes reference design tokens
<div className="bg-primary rounded-md p-6 text-sm">
```

### CSS Theme Configuration

Use Tailwind v4 `@theme` blocks in CSS, not `tailwind.config.ts`.

```css
/* GOOD: Tailwind v4 @theme block */
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.6 0.2 260);
  --color-destructive: oklch(0.6 0.2 25);
  --radius-md: 0.375rem;
  --font-sans: "Inter", sans-serif;
}
```

### Class Merging with cn()

Always use `cn()` from `@/lib/utils` to merge classes. Never concatenate class strings manually.

```typescript
import { cn } from "@/lib/utils"

// BAD: String concatenation or template literals
<div className={"card " + (active ? "active" : "")}>
<div className={`card ${active ? "active" : ""}`}>

// GOOD: cn() handles conflicts and conditionals
<div className={cn("rounded-md border", active && "ring-2 ring-primary")}>
```

---

## 6. shadcn/ui Components

### Import Convention

Import shadcn/ui components from `@/components/ui/`. Do not recreate components that shadcn already provides.

```typescript
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Dialog, DialogContent } from "@/components/ui/dialog"
```

### Icons

Use Lucide React icons only. Do not use Material Icons or other icon libraries.

```typescript
import { AlertTriangle, Check, X } from "lucide-react"
```

### Component Extension with CVA

Extend shadcn/ui components for project-specific needs. Use CVA (class-variance-authority) for variants.

```typescript
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva("inline-flex items-center justify-center", {
  variants: {
    intent: {
      primary: "bg-primary text-primary-foreground hover:bg-primary/90",
      destructive: "bg-destructive text-destructive-foreground",
      ghost: "hover:bg-accent hover:text-accent-foreground",
    },
    size: {
      sm: "h-8 px-3 text-xs",
      md: "h-10 px-4 text-sm",
      lg: "h-12 px-6 text-base",
    },
  },
  defaultVariants: {
    intent: "primary",
    size: "md",
  },
})
```

### Typed Component with Variants (AlertCard)

Compose shadcn/ui primitives into domain-specific components.

```typescript
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { AlertTriangle, Info } from "lucide-react"

const alertCardVariants = cva("", {
  variants: {
    severity: {
      critical: "border-destructive",
      warning: "border-yellow-500",
      info: "border-primary",
    },
  },
  defaultVariants: {
    severity: "info",
  },
})

interface AlertCardProps extends VariantProps<typeof alertCardVariants> {
  title: string
  description: string
  className?: string
}

function AlertCard({ title, description, severity, className }: AlertCardProps) {
  return (
    <Card className={cn(alertCardVariants({ severity }), className)}>
      <CardHeader className="flex flex-row items-center gap-2">
        {severity === "critical" ? (
          <AlertTriangle className="h-4 w-4 text-destructive" />
        ) : (
          <Info className="h-4 w-4 text-primary" />
        )}
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}
```

### Component Extension Pattern (ActionButton)

Wrap shadcn/ui components to add domain behavior while keeping the base component swappable.

```typescript
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

interface ActionButtonProps {
  loading?: boolean
  children: React.ReactNode
  onClick: () => void
}

function ActionButton({ loading, children, onClick }: ActionButtonProps) {
  return (
    <Button onClick={onClick} disabled={loading}>
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </Button>
  )
}
```

### Design Token Usage in Components

Reference tokens through semantic Tailwind classes, never through hardcoded values. Tokens are defined in the CSS `@theme` block (from design-workflow token pipeline).

```typescript
// Tokens flow: Pencil variables -> w3c.json -> Style Dictionary -> @theme -> Tailwind classes

// GOOD: Semantic classes that reference tokens
<div className="bg-card text-card-foreground rounded-lg p-6 shadow-md">
  <h2 className="text-lg font-semibold text-foreground">{title}</h2>
  <p className="text-sm text-muted-foreground">{description}</p>
</div>

// BAD: Hardcoded values that bypass the design system
<div className="bg-white text-gray-900 rounded-lg p-6 shadow-md">
```

---

## 7. Common Patterns

### API Response Format

Use a consistent envelope for all API responses.

```typescript
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  meta?: {
    total: number
    page: number
    limit: number
  }
}
```

### Custom Hooks Pattern

```typescript
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}
```

### Repository Pattern

Encapsulate data access behind a consistent interface.

```typescript
interface Repository<T> {
  findAll(filters?: Filters): Promise<T[]>
  findById(id: string): Promise<T | null>
  create(data: CreateDto): Promise<T>
  update(id: string, data: UpdateDto): Promise<T>
  delete(id: string): Promise<void>
}
```

---

## 8. Security

### Secret Management

Never hardcode secrets. Use environment variables with startup validation.

```typescript
// BAD: Hardcoded secrets
const openAiCredential = "sk-abc123"

// GOOD: Environment variables with validation
const openAiApiKey = process.env.OPENAI_API_KEY

if (!openAiApiKey) {
  throw new Error('OPENAI_API_KEY not configured')
}
```

---

## Lint Configuration

Enforce Tailwind/shadcn constraints at lint time:

```bash
npm install --save-dev eslint-plugin-tailwindcss
```

```javascript
// eslint.config.js
{
  rules: {
    "tailwindcss/no-custom-classname": "error",  // blocks bg-[#hex], w-[375px], etc.
    "tailwindcss/classnames-order": "warn",       // consistent class ordering
  }
}
```
