# 语言规范

## Python

- **风格**：PEP 8 + 类型注解；优先不可变数据结构（`@dataclass(frozen=True)`、`NamedTuple`）
- **工具**：black + isort + ruff；pytest（`pytest --cov=src`）
- **环境变量**：`os.environ["KEY"]`（缺失时 KeyError）— 禁止静默默认值 → Hook: `post-write-quality.sh`
→ python-patterns skill / django-security skill / python-testing skill

## TypeScript

- **类型**：`interface` 用于可扩展结构；`type` 用于联合/交叉/映射类型；字符串字面量联合而非 `enum`；避免 `any`（用 `unknown` 收窄）；不使用 `React.FC` → Hook: `post-write-quality.sh`
- **UI**：Tailwind v4 语义类 + `cn()`；shadcn/ui 从 `@/components/ui/` 导入；仅用 Lucide 图标
- **验证**：Zod schema + `z.infer` 推导类型
- **环境变量**：`process.env.KEY` 启动时显式验证—缺失时抛出异常
- **测试**：Vitest + React Testing Library；E2E 用 Playwright（前端关键用户旅程）；API Mock 用 MSW；禁止直接 mock fetch/axios
→ typescript-patterns skill / typescript-testing skill
