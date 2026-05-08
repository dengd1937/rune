#!/usr/bin/env python3
# Trigger:  PreToolUse — matcher: Bash
# Behavior: HARD BLOCK if `git commit` runs without a reviewer call
#           since the last commit. Exit 2 = block, exit 0 = allow.
# Override: export SKIP_REVIEW_CHECK=1  (emergency only)
#
# Detection (粗粒度兜底，不校验 verdict)：
#   工具名匹配 "Task" 或 "Agent"（Claude Code 实际名为 Agent，
#   "Task" 保留兼容其他 harness），并满足下列任一：
#   1. Named reviewer agent: subagent_type 含 "reviewer"
#      (code-reviewer / security-reviewer / python-reviewer / ...)
#   2. 新流程 general-purpose + reviewer prompt 模板:
#      subagent_type == "general-purpose" 且 prompt 含 GP_REVIEWER_PROMPTS 中任一文件名
#
# 设计角色：仅检测"是否调用过 reviewer"。verdict / diff 一致性 / 时效性
#           校验由 task-driven-development skill 的修复闭环兜底，hook 不做。

import json
import os
import re
import sys

REVIEW_KEYWORD = "reviewer"
GP_REVIEWER_PROMPTS = (
    "code-quality-reviewer-prompt.md",
    "spec-reviewer-prompt.md",
)

SOURCE_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts",
    ".go", ".rs", ".java", ".rb", ".cs", ".cpp", ".c", ".h", ".hpp",
    ".swift", ".kt", ".scala", ".dart", ".php", ".lua",
    ".vue", ".svelte", ".html", ".css", ".scss", ".sql",
}

EXEMPT_RE = re.compile(
    r"(tests?/|__tests__/|test_fixtures?/|spec/|scripts?/|\.env\.example)"
)

GIT_COMMIT_RE = re.compile(r"(^|[;&|]\s*)\s*git\s+commit\b")


def main() -> None:
    if os.environ.get("SKIP_REVIEW_CHECK") == "1":
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    cmd: str = payload.get("tool_input", {}).get("command", "")
    first_line = cmd.split("\n", 1)[0]
    if not GIT_COMMIT_RE.search(first_line):
        sys.exit(0)

    transcript: str = payload.get("transcript_path", "")
    if not transcript or not os.path.isfile(transcript):
        sys.exit(0)

    try:
        with open(transcript) as f:
            lines = f.readlines()
    except Exception:
        sys.exit(0)

    # Pass 1 (forward): collect tool_use_ids whose tool_result was an error.
    # Used to skip failed `git commit` calls so they don't act as window
    # boundaries — otherwise a hook-blocked retry would always fail.
    failed_tool_ids: set[str] = set()
    for raw in lines:
        try:
            entry = json.loads(raw)
        except Exception:
            continue
        if entry.get("type") != "user":
            continue
        content = entry.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") == "tool_result" and block.get("is_error"):
                tid = block.get("tool_use_id")
                if tid:
                    failed_tool_ids.add(tid)

    # Pass 2 (backward): collect Write/Edit on source files and reviewer
    # Task/Agent calls. Stop at the previous *successful* `git commit` Bash call.
    edited_files: list[str] = []
    saw_reviewer = False

    for raw in reversed(lines):
        try:
            entry = json.loads(raw)
        except Exception:
            continue

        if entry.get("type") != "assistant":
            continue

        content = entry.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if block.get("type") != "tool_use":
                continue

            name: str = block.get("name", "")
            inp: dict = block.get("input", {})

            if name == "Bash":
                bash_first = inp.get("command", "").split("\n", 1)[0]
                if GIT_COMMIT_RE.search(bash_first):
                    if block.get("id") in failed_tool_ids:
                        # Failed git commit (hook-blocked, etc.) — not a
                        # boundary; keep scanning earlier turns.
                        continue
                    # Reached previous successful commit — window boundary
                    _emit(edited_files, saw_reviewer)
                    return

            elif name in ("Write", "Edit"):
                fp: str = inp.get("file_path", "")
                if _is_source(fp):
                    edited_files.append(fp)

            elif name in ("Task", "Agent"):
                # Claude Code uses "Agent" as the actual tool name; "Task"
                # kept for forward/backward compat with other harnesses.
                sub: str = str(inp.get("subagent_type", "")).lower()
                prompt_text: str = str(inp.get("prompt", ""))

                if REVIEW_KEYWORD in sub:
                    saw_reviewer = True
                elif "general-purpose" in sub and any(
                    p in prompt_text for p in GP_REVIEWER_PROMPTS
                ):
                    saw_reviewer = True

    _emit(edited_files, saw_reviewer)


def _is_source(path: str) -> bool:
    if not path or EXEMPT_RE.search(path):
        return False
    _, ext = os.path.splitext(path)
    return ext.lower() in SOURCE_EXTS


def _emit(files: list[str], saw_reviewer: bool) -> None:
    if saw_reviewer or not files:
        sys.exit(0)

    unique = list(dict.fromkeys(files))
    listed = "\n  - ".join(unique[:5])
    suffix = f"\n  ... and {len(unique) - 5} more" if len(unique) > 5 else ""

    print(
        "[hook] BLOCKED: no reviewer was invoked since last commit.\n"
        f"Modified source files:\n"
        f"  - {listed}{suffix}\n"
        "合规路径任选其一：\n"
        "  (A) Task(subagent_type=\"general-purpose\") + code-quality-reviewer-prompt.md\n"
        "      （task-driven-development skill 的标准 Step 4 通用质量审查）\n"
        "  (B) 调用 named reviewer：security-reviewer / python-reviewer / typescript-reviewer\n"
        "Emergency override: export SKIP_REVIEW_CHECK=1",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
