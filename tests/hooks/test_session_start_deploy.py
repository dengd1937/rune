"""Tests for hooks/session-start commit-msg hook deployment side-effect.

session-start also deploys a commit-msg wrapper into the project's
.git/hooks/commit-msg (idempotent; never overwrites a non-Rune hook). These
tests drive that side-effect against a throwaway git repo.
"""
import os

from conftest import run_hook


def _run_deploy(repo):
    return run_hook("session-start", "", env={"CLAUDE_PROJECT_DIR": str(repo)}, cwd=repo)


def test_deploy_creates_commit_msg_hook(tmp_repo):
    res = _run_deploy(tmp_repo)
    assert res.exit_code == 0
    hook = tmp_repo / ".git/hooks/commit-msg"
    assert hook.exists()
    assert os.access(hook, os.X_OK)
    content = hook.read_text()
    assert "Auto-deployed by Rune" in content
    assert "commit-msg-strip-coauthor" in content


def test_deploy_is_idempotent(tmp_repo):
    _run_deploy(tmp_repo)
    hook = tmp_repo / ".git/hooks/commit-msg"
    _run_deploy(tmp_repo)  # second run updates path, keeps it Rune's
    assert hook.exists()
    assert "Auto-deployed by Rune" in hook.read_text()


def test_deploy_preserves_non_rune_hook(tmp_repo):
    hook = tmp_repo / ".git/hooks/commit-msg"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text("#!/bin/sh\n# my custom hook\necho custom\n")
    hook.chmod(0o755)
    _run_deploy(tmp_repo)
    content = hook.read_text()
    assert "Auto-deployed by Rune" not in content
    assert "my custom hook" in content


def test_deploy_no_crash_in_non_git_dir(tmp_path):
    res = run_hook("session-start", "", env={"CLAUDE_PROJECT_DIR": str(tmp_path)}, cwd=tmp_path)
    assert res.exit_code == 0
