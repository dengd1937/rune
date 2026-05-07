# 通用规范

## 代码质量

- **不可变性（CRITICAL）**：永远创建新对象，禁止原地修改 → python-patterns skill / typescript-patterns skill
- **文件组织**：多小文件 > 少大文件；高内聚低耦合；典型 200-400 行，最大 800 行 → Hook: `post-write-quality.sh`
- **错误处理**：每一层显式处理；永不静默吞掉 → python-patterns skill / typescript-patterns skill
- **输入验证**：系统边界验证，schema 验证，快速失败 → python-patterns skill / typescript-patterns skill
- **外科手术式修改**：每行改动对应任务；发现无关死代码告知用户而非擅自删除
→ code-quality-gate skill

## 架构模式

- **骨架项目**：搜索成熟模板 → 并行 agent 评估 → 克隆最优方案迭代
- **Repository 模式**：数据访问封装在标准接口后，业务逻辑依赖抽象 → typescript-patterns skill
- **API 响应格式**：统一信封（成功标志、数据载荷、错误字段、分页元数据）→ typescript-patterns skill
- **架构决策记录**：涉及技术选型、模块边界、数据模型、API 契约的变更应产出 ADR（`docs/architecture/adr/`）→ architect skill

## 安全

密钥由 `pre-write-secrets.sh` 物理拦截。以下情况触发 security-reviewer agent：
- 认证/授权代码、用户输入处理、数据库查询、文件系统操作
- 外部 API 调用、加密操作、支付/金融代码

发现安全问题：立即停下 → security-reviewer agent → 修复 CRITICAL → 轮换密钥 → 排查同类
→ security-reviewer skill

## 测试

最低覆盖率 **80%**（单元 + 集成 + E2E）。强制 RED → GREEN → IMPROVE。
→ tdd-workflow skill

## Red Flags — 代码质量偷懒的合理化借口

| 借口 | 现实 |
|---|---|
| "原地修改对象更省内存/更直观" | 不可变性是 CRITICAL；永远创建新对象，例外需用户批准 |
| "这个文件 1200 行还行，逻辑都相关" | 超过 800 行触发拆分（hook 会标记），相关 ≠ 同文件 |
| "环境变量缺失给个空字符串/默认值更友好" | 必须抛异常/KeyError，静默默认值会让生产环境带病运行 |
| "异常先 catch 住，不影响主流程" | 静默吞异常不允许；每层显式处理或重抛 |
| "我顺手清理了一些死代码" | 外科手术式：发现无关死代码先告知用户，不擅自删除 |
| "这只是临时测试脚本，跑完再说" | 临时脚本（test_*.py、verify_*.py）执行后**立即**删除 |
| "secrets 写死也行，反正只是 dev/示例" | pre-write-secrets.sh 物理拦截，不存在"只是 dev"豁免 |
| "测试覆盖率差不多 70% 也够了" | 最低 80%，达不到不算完成 |
| "这层不需要输入验证，调用方已经验过了" | 系统边界必须验证；信任外部输入是漏洞起点 |
| "用 dict 传参更灵活，比 dataclass 方便" | 优先强类型；非结构化 dict 是 Python 代码腐败的源头 |
