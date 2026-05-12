---
name: review-handling
description: Use when code-review returns BLOCK — processes feedback, deduplicates, classifies, orders, and evaluates pushback before routing to implementer for fixes
---

# Review Handling

处理 code-review 返回的 BLOCK 反馈。不直接修复代码——输出结构化的修复指令，由 implementer 执行。

**启动时公告：** "使用 review-handling skill 处理审查反馈。"

---

## 处理流程

```
code-review 返回 BLOCK
        │
        ▼
   1. 去重
        │
        ▼
   2. 分类
        │
        ▼
   3. 冲突检测
        │
        ▼
   4. Pushback 评估
        │
        ▼
   5. 输出修复指令
```

### 1. 去重

多个 reviewer 可能标记同一问题。合并：
- 相同文件:行号 + 相同问题描述 → 合并为一条
- 同类问题（"3 个函数缺 error handling"）→ 合并为一条摘要，附完整位置列表

### 2. 分类

| 类别 | 定义 | 示例 |
|------|------|------|
| blocking | 安全漏洞、功能缺失、数据丢失风险 | SQL 注入、未处理异常、逻辑错误 |
| simple | typo、import 缺失、命名不当 | 变量名拼写、遗漏 import、调试残留 |
| complex | 逻辑重构、架构调整、模式变更 | 提取公共函数、修改数据流、更换实现模式 |

### 3. 冲突检测

当多个 reviewer 意见矛盾时：

```
冲突示例：
  reviewer A: "这里加缓存提高性能"
  reviewer B: "不要过早抽象，保持简单"

处理：标记为冲突，两个建议都列给 implementer，由 implementer 根据上下文判断。
不自行决定采纳哪一方。
```

### 4. Pushback 评估

逐条检查每条反馈，评估是否属于疑似误报：

**可能 pushback 的情况：**
- reviewer 建议的修改与代码库现有模式矛盾（代码库用 A 模式，reviewer 要求改成 B）
- reviewer 要求添加 diff 范围外的功能（YAGNI）——grep 代码库确认无调用方
- reviewer 对业务逻辑的理解与实现意图不一致
- reviewer 建议的修改会破坏现有测试

**pushback 处理：**
- 标记为"疑似误报"
- 附具体理由（引用代码/测试/现有模式）
- **由用户确认**，不自行驳回

**CRITICAL 和 HIGH 级别的反馈不标记为"疑似误报"**——只有 MEDIUM/LOW 可以评估 pushback。

### 5. 输出修复指令

按 **blocking → simple → complex** 排序，每条包含：

```
[blocking] SQL 注入漏洞
File: src/api/users.ts:42
Issue: userId 未参数化，直接拼接到 SQL
Fix: 使用参数化查询 $1 替代字符串拼接

[simple] 调试日志残留
File: src/utils/helper.ts:15
Issue: console.log 未清理
Fix: 移除该行

[complex] 提取公共验证逻辑
Files: src/api/users.ts:30, src/api/orders.ts:55
Issue: 两个 endpoint 重复了相同的输入验证
Fix: 提取为 validateInput() 工具函数

[疑似误报] 建议加缓存层
File: src/services/search.ts:78
Issue: reviewer 建议对搜索结果加缓存
理由: grep 代码库无重复调用场景，当前为单次查询，YAGNI
→ 待用户确认
```

---

## 修复循环

修复指令输出后，由调用方（SDD / investigate）派发 implementer 执行修复：

```
修复指令 → implementer 修复 → /code-quality-gate → /code-review
                                                        │
                                                    APPROVE → 继续
                                                    BLOCK → 重新 /review-handling
```

**关键规则：**
- implementer 按修复指令逐条修复，不添加额外改动
- 修复完成后重跑完整 code-quality-gate + code-review
- 不跳过重审步骤

---

## 适用场景

| 场景 | 来源 |
|------|------|
| SDD 逐任务审查 BLOCK | code-review (per-task) |
| SDD 全局终审 BLOCK | code-review (global) |
| investigate 修复后审查 BLOCK | code-review (per-task) |
| 人类 PR 审查反馈 | 外部反馈（同样适用去重、分类、排序） |

## 行为规范

### 禁止表演性同意

处理审查反馈时的沟通规范：

**不允许：**
- "好的"、"你说得对"、"有道理" — 情绪性回应
- "感谢指出" / "谢谢" — 感谢表达
- "我来实现这个" — 未经验证就同意

**允许：**
- "已修复。[具体改了什么]"
- "验证后发现 [技术理由]"
- 直接开始工作（行动 > 言语）

**原则：** 代码本身证明你听到了反馈，不需要用语言表达。

### YAGNI Check

当 reviewer 建议添加功能/抽象/优化时：

1. grep 代码库确认有实际调用方
2. 无调用方 → 标记为"疑似误报" + 理由："grep 无实际使用场景，YAGNI"
3. 有调用方 → 按正常流程处理

此检查融入现有 pushback 评估步骤（处理流程第 4 步），不单独成步骤。

### 不清楚先问，不部分实现

已有此规则（禁止段落），此处补充具体示例：

```
reviewer 指出 5 个问题，理解其中 4 个，第 5 个不清楚：

✅ "理解问题 1-4，问题 5 的 [具体描述] 需要澄清：[具体问题]"
❌ 先修 4 个，第 5 个"后面再说"
```

**原因：** 问题之间可能有关联。部分理解 = 错误实现。

### Pushback 后的纠正方式

标记为"疑似误报"后的处理：

**pushback 被确认需要修复时：**
- "检查了 [X]，确认 [Y]。现在修复。"
- 不辩护为什么之前 pushback
- 不长篇道歉

**pushback 被接受（确认是误报）时：**
- 不表达情绪，继续下一步

---

## 禁止

- 不清楚时部分实现——先问清楚所有不清楚的项，再开始修复
- 自行驳回 CRITICAL/HIGH 级别的反馈——必须用户确认
- 批量修复不逐个验证——每条修复后确认效果
- 添加修复指令范围外的改动——外科手术式

---

## Red Flags

| 借口 | 现实 |
|------|------|
| "reviewer 误报了，跳过" | 误报需具体理由 + 用户确认，不许自行驳回 |
| "先修一部分，其他的后面再说" | 不清楚的部分先问，不部分实现 |
| "这些反馈太琐碎，一起改" | 逐条修复，逐条验证 |
| "我顺手把那个也改了" | 外科手术式：只改 reviewer 指出的位置 |
| "连续 3 次还 BLOCK，reviewer 太严" | 可能是架构问题，与用户讨论而非继续试修 |
