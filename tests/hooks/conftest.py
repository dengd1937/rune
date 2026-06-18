"""Shared fixtures for Rune hook unit tests (A-layer).

Each hook is treated as a black box: stdin JSON in → (exit code, stderr) out.
Hooks are invoked via subprocess (python3 for *.py, bash otherwise) with
CLAUDE_PLUGIN_ROOT pinned to the repo root, so they resolve paths / source
lib/utils.sh / find SKILL.md exactly as in production. Tests never call an LLM.
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

# tests/hooks/conftest.py -> parents[2] = repo root.
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = PLUGIN_ROOT / "hooks"


@dataclass
class HookResult:
    """Captured outcome of one hook invocation."""

    exit_code: int
    stdout: str
    stderr: str

    @property
    def allowed(self) -> bool:
        """exit 0 = hook permits the tool call."""
        return self.exit_code == 0

    @property
    def blocked(self) -> bool:
        """exit 2 = hook hard-blocks the tool call (PreToolUse convention)."""
        return self.exit_code == 2

    @property
    def warned(self) -> bool:
        """advisory hooks exit 0 but emit a WARNING line."""
        return self.allowed and "WARNING" in self.stderr

    def has_block_msg(self, substr: str) -> bool:
        return self.blocked and substr in self.stderr

    def has_warning(self, substr: str) -> bool:
        return self.warned and substr in self.stderr


def _interpreter_for(hook_path: Path) -> list[str]:
    return ["python3"] if hook_path.suffix == ".py" else ["bash"]


def run_hook(
    name: str,
    stdin: str,
    *,
    env: dict[str, str] | None = None,
    cwd: Path | str | None = None,
) -> HookResult:
    """Invoke a hook by filename (under hooks/), feeding stdin JSON.

    CLAUDE_PLUGIN_ROOT is always pinned to PLUGIN_ROOT; caller env is merged
    on top so individual tests can override CLAUDE_PROJECT_DIR, SKIP_* etc.
    """
    hook_path = HOOKS_DIR / name
    full_env = dict(os.environ)
    full_env["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    if env:
        full_env.update(env)

    proc = subprocess.run(
        [*_interpreter_for(hook_path), str(hook_path)],
        input=stdin,
        capture_output=True,
        text=True,
        env=full_env,
        cwd=str(cwd) if cwd else None,
    )
    return HookResult(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def hook_stdin(
    tool_name: str,
    *,
    transcript_path: str | None = None,
    **tool_input: Any,
) -> str:
    """Build the JSON payload a Claude Code hook receives on stdin."""
    payload: dict[str, Any] = {"tool_name": tool_name, "tool_input": tool_input}
    if transcript_path is not None:
        payload["transcript_path"] = transcript_path
    return json.dumps(payload)


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """A throwaway git repo (user configured) for hooks that need git state."""
    for args in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "test@test.com"],
        ["git", "config", "user.name", "Test"],
    ):
        subprocess.run(args, cwd=tmp_path, check=True)
    return tmp_path
