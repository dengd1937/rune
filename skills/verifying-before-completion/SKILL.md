---
name: verifying-before-completion
description: Use when about to declare an implementation, fix, or quality-gate run complete — run a fresh build/test/lint verification command in the same turn and read its output before stating success.
origin: rune
---

# Verifying Before Completion

声明完成前的横切诚信门。任何即将"宣称完成 / 通过 / 已修 / 正常工作"的时刻，必须在当前消息内跑过验证命令并读完输出。

**启动时公告：** "使用 verifying-before-completion skill 跑验证命令。"

**核心原则：** Evidence before claims, always.

---

## 铁律

```
没有在当前消息内跑过验证命令 → 不许声称该项通过
```

违反字面就是违反精神。这条不与 IRON LAW L1/L3 并列，而是 L3 "未通过审查的代码不许 commit" 的**前置补强** —— L3 守 commit 时点，本 skill 守 commit 之前的每个 claim 时点。

---

## 触发场景

任何即将打出以下措辞之前，**必须**先 invoke 本 skill：

- "测试通过 / tests pass / passing"
- "build 成功 / build succeeds"
- "lint clean / no errors"
- "bug 修好 / fix works / 已修复"
- "完成 / done / finished"
- "通过 / 验证通过 / 已验证"
- "看起来对 / 应该过 / should work / looks correct"

以及以下流程节点（钩子触发）：

| 节点 | 验证内容 |
|---|---|
| `investigate` 4b GREEN 后 | 当前消息内跑原复现测试，确认 PASS |
| `investigate` 4c IMPROVE 后 | 当前消息内重跑 RED→GREEN 测试套件，确认未回归 |
| `investigate` 4f 回 4d 之前 | 当前消息内跑复现测试 + 每层防御独立测试 |
| `code-quality-gate` 通过声明前 | 当前消息内有 lint/format/typecheck 完整输出 |
| 接收 subagent DONE 报告时 | `git diff` 看实际改动 + 跑相关测试（详见下文 Subagent 场景） |
| commit / push / PR 创建前 | 全量测试套件 + 覆盖率（与 `commit-quality` 串联，详见下文） |

---

## Gate 函数（声明前 5 步）

```
1. IDENTIFY — 什么命令能证明这个声明？
2. RUN     — 在当前消息内执行完整命令（禁止复用历史输出）
3. READ    — 读完整 output、检查 exit code、清点 failure 数
4. VERIFY  — output 是否真的支持该声明？
              ├─ 不支持 → 报告实际状态（附 evidence）
              └─ 支持   → 带 evidence 做声明
5. CLAIM   — 才允许说 "done / pass / 修好了"
```

**跳过任一步 = 撒谎，不是验证。**

---

## 声明 vs evidence 对照

| 声明 | 必备 evidence | 不够 |
|---|---|---|
| 测试通过 | 测试命令完整 output + 0 failures | 历史运行 / "应该过" |
| Lint 干净 | linter 当前 output + 0 errors | 部分检查 / 推断 |
| Build 成功 | build 命令 + exit 0 | "linter 过了" |
| Bug 修好 | 原 bug 复现路径测试 PASS | 改了代码就假设 |
| 回归测试有效 | red-green 双向验证（revert fix → fail → restore → pass） | 跑一次就过 |
| Subagent 完成 | `git diff` 看实际改动 + 测试 fresh PASS | subagent 自报 success |
| 需求满足 | 逐条 checklist 验证 | 测试整体过了 |

---

## Red Flags — 出现立刻停

- 说 "should / probably / seems to / 应该 / 大概 / 看起来"
- 跑命令前已经在打"完成感"措辞（"很好""完美""done""搞定"）
- 准备 commit / push / PR 但当前消息没验证 output
- 信任 subagent 自报 success 不去 diff
- "局部检查就够 / 只是这次跳过"
- 累了想结束

---

## 反 rationalization

| 借口 | 现实 |
|---|---|
| "应该过了" | RUN 命令 |
| "我有信心" | 信心 ≠ evidence |
| "就这一次" | 没有例外 |
| "linter 过了 = 编译过了" | linter 不查编译 |
| "subagent 说成功" | 独立验证 diff |
| "累了" | 累 ≠ 借口 |
| "局部检查够用" | 局部不能证明整体 |
| "措辞不一样规则不适用" | 精神高于字面 |
| "我已经手动测过了" | 手动测试无记录、不可重放、不算 evidence |

---

## Subagent 场景的推荐补强

**触发条件：** 主代理接收 implementer/reviewer subagent 的 DONE/APPROVE 报告，且即将基于该报告进入下一流程节点（如 SDD Step 2/3、Phase 6 收尾）时。

**推荐补强（非硬改 SDD 控制流）：**

1. `git diff <base_SHA>..<head_SHA>` —— 确认 subagent 真改了它声称改的文件
2. 跑 subagent 应该已经跑过的测试命令 —— 不复用 subagent 的 output
3. 如果 diff 为空或与报告不符 → 视为 BLOCK，要求 subagent 重新执行（与 SDD 既有 BLOCKED 状态处理一致）

这条是 SDD "trust but verify" 原则的横切补强建议，**不修改 SDD 流程控制本身**。SDD skill 中既有的 Step 1 状态处理（DONE/BLOCKED/NEEDS_CONTEXT）保持原样；本节为主代理在收到 DONE 时提供推荐的 verify 动作清单。

---

## 与既有 skill 的边界

- **`code-quality-gate`**：跑命令本身被该 skill 包装；本 skill 要求的是"宣称 quality-gate 通过前必须有 fresh 命令输出"
- **`code-review`**：reviewer subagent 报 APPROVE 后，主代理仍需 verify reviewer 真看了 diff（看 reviewer 报告里有没有引用具体 file:line），而非盲信 verdict
- **`commit-quality`**：负责 commit 前 lint staged 文件 + secrets 扫描；本 skill 补强其前序步骤——`commit-quality` 触发前必须已有全量测试 PASS 输出作为 evidence（fresh 输出，不复用历史）
- **`code-quality-gate` vs `commit-quality`**：前者按文件改动后触发（任务内的 lint/format/typecheck），后者按 commit 前触发（staged-only lint + secrets）；本 skill 在两者之间作为诚信门串联使用

---

## Bottom Line

**跑命令 → 读输出 → 然后才声明。**

This is non-negotiable.
