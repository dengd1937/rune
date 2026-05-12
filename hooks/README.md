# Claude Code Hooks

项目级 hook 层，提供**确定性**的安全和质量兜底。

## Hooks 清单

| 脚本 | 触发时机 | 阻塞？ | 作用 |
|---|---|---|---|
| `pre-bash-guard.sh` | PreToolUse[Bash] | 硬阻塞 | 拦截危险 git 命令、错误包管理器 |
| `pre-write-secrets.sh` | PreToolUse[Write\|Edit] | 硬阻塞 | 扫描密钥/私钥写入源码 |
| `post-write-debug.sh` | PostToolUse[Write\|Edit] | 软警告 | 检测新增调试语句 |
| `pre-commit-review-check.py` | PreToolUse[Bash] | 硬阻塞 | git commit 前检查 code-reviewer 是否被调用 |

## 禁用单个 Hook

```bash
chmod -x hooks/<hook-name>.sh   # 禁用（.sh 脚本）
chmod -x hooks/<hook-name>.py   # 禁用（.py 脚本）
chmod +x hooks/<hook-name>.*    # 重新启用
```

`pre-commit-review-check.py` 也支持会话级跳过（无需修改文件权限）：

```bash
export SKIP_REVIEW_CHECK=1   # 本次 shell 会话内跳过提醒
```

## 测试方法

```bash
# 测试 1：应阻塞 — git commit --no-verify
echo '{"tool_name":"Bash","tool_input":{"command":"git commit --no-verify -m test"}}' \
  | bash hooks/pre-bash-guard.sh
# 预期：exit 2，stderr 含 [hook] BLOCKED

# 测试 2：应放行 — 普通命令
echo '{"tool_name":"Bash","tool_input":{"command":"git log --oneline"}}' \
  | bash hooks/pre-bash-guard.sh
# 预期：exit 0，无输出

# 测试 3：应阻塞 — API key 写入源码（用 <REDACTED> 代替真实格式以避免触发 hook）
#   实际格式: const key = "sk-" + "abc...xyz"（32+ 字符）
echo '{"tool_name":"Write","tool_input":{"file_path":"src/config.ts","content":"const key = \"sk-<REDACTED>\""}}' \
  | bash hooks/pre-write-secrets.sh
# 预期：exit 0（因为 <REDACTED> 不满足正则），改用真实格式时会 exit 2

# 测试 4：应放行 — .env.example 豁免
echo '{"tool_name":"Write","tool_input":{"file_path":".env.example","content":"OPENAI_API_KEY=sk-your-key-here"}}' \
  | bash hooks/pre-write-secrets.sh
# 预期：exit 0，路径豁免

# 测试 5：调试语句软警告
echo '{"tool_name":"Edit","tool_input":{"file_path":"src/app.ts","old_string":"","new_string":"console.log(user)"}}' \
  | bash hooks/post-write-debug.sh
# 预期：exit 0，stderr 含 [hook] WARNING

# 测试 6：pip install 在 Python 项目中应阻塞（需有 pyproject.toml）
echo '{"tool_name":"Bash","tool_input":{"command":"pip install requests"}}' \
  | bash hooks/pre-bash-guard.sh
# 预期（有 pyproject.toml）：exit 2；（无 pyproject.toml）：exit 0

# 测试 7：git commit + 无 reviewer → BLOCKED（需 transcript_path 指向含 Edit 记录的 JSONL）
# 测试 8：git commit + reviewer 已调用 → silent（JSONL 含 Task(code-reviewer)）
# 测试 9：SKIP_REVIEW_CHECK=1 时总是 silent
#   SKIP_REVIEW_CHECK=1 echo '...' | python3 hooks/pre-commit-review-check.py
# 预期：exit 0，无输出
```

## 通用性说明

- 全部 `#!/usr/bin/env bash`，兼容 macOS / Linux / WSL
- 只依赖 `python3`（探测失败则 silent skip）
- `pip/poetry/conda` 拦截仅在存在 `pyproject.toml` / `setup.py` / `requirements.txt` 时生效
- 路径通过 `${CLAUDE_PLUGIN_ROOT}` 引用，支持任意安装路径
