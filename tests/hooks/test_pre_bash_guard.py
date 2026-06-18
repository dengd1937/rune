"""Tests for hooks/pre-bash-guard.sh — BLOCKS dangerous git/rm/package + non-conventional commits.

Anchor: header comment (BLOCKS dangerous git commands, catastrophic rm -rf,
wrong package manager usage, and non-Conventional-Commit messages).
"""
from conftest import hook_stdin, run_hook

import pytest


def run(cmd, **kw):
    return run_hook("pre-bash-guard.sh", hook_stdin("Bash", command=cmd), **kw)


# ── Rule 1: --no-verify ───────────────────────────────────────────────────────
def test_no_verify_blocked():
    assert run('git commit --no-verify -m "feat: x"').blocked


def test_commit_without_no_verify_allowed():
    assert run('git commit -m "feat: x"').allowed


# ── Rule 2: force-push to main/master ─────────────────────────────────────────
def test_force_push_main_blocked():
    assert run("git push --force origin main").blocked


def test_force_push_master_blocked():
    assert run("git push --force origin master").blocked


def test_short_force_main_blocked():
    assert run("git push -f origin main").blocked


def test_force_push_feature_branch_allowed():
    assert run("git push --force origin feature").allowed


# ── Rule 3: git reset --hard ──────────────────────────────────────────────────
def test_reset_hard_blocked():
    assert run("git reset --hard").blocked


def test_reset_soft_allowed():
    assert run("git reset --soft HEAD~1").allowed


# ── Rule 4: catastrophic rm -rf ───────────────────────────────────────────────
@pytest.mark.parametrize(
    "cmd",
    ["rm -rf /", "rm -rf /home", "rm -rf /etc", "rm -rf ~", "rm -rf *", "rm -rf .."],
    ids=["root", "abs-home", "abs-etc", "home", "star", "dotdot"],
)
def test_rm_rf_dangerous_target_blocked(cmd):
    # any target starting with / ~ * or .. is treated as catastrophic
    assert run(cmd).blocked


@pytest.mark.parametrize(
    "cmd",
    ["rm -rf ./build", "rm -rf dist", "rm -rf node_modules"],
    ids=["relative-dot", "named-dir", "named-modules"],
)
def test_rm_rf_precise_target_allowed(cmd):
    # relative/named targets are allowed
    assert run(cmd).allowed


# ── Rule 5: package manager (python projects only) ────────────────────────────
def test_pip_install_non_python_project_allowed(tmp_path):
    # no pyproject.toml/setup.py/requirements.txt -> not a python project
    res = run("pip install requests", env={"CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert res.allowed


def test_pip_install_python_project_blocked(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    res = run("pip install requests", env={"CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert res.blocked


def test_uv_add_python_project_allowed(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    res = run("uv add requests", env={"CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert res.allowed


# ── Rule 6: Conventional Commits ──────────────────────────────────────────────
@pytest.mark.parametrize(
    "msg",
    ["feat: add thing", "fix(auth): handle null", "chore!: drop legacy", "refactor(core): x", "docs: readme"],
    ids=["feat", "fix-scope", "breaking", "refactor", "docs"],
)
def test_valid_conventional_commit_allowed(msg):
    assert run(f'git commit -m "{msg}"').allowed


@pytest.mark.parametrize(
    "msg", ["updated stuff", "feat x", "Feat: capitalized"],
    ids=["no-type", "no-colon", "capitalized"],
)
def test_invalid_commit_message_blocked(msg):
    assert run(f'git commit -m "{msg}"').blocked


def test_heredoc_commit_message_valid():
    cmd = 'git commit -m "$(cat <<\'EOF\'\nfeat: heredoc works\nEOF\n)"'
    assert run(cmd).allowed


def test_heredoc_commit_message_invalid():
    cmd = 'git commit -m "$(cat <<\'EOF\'\njust some words\nEOF\n)"'
    assert run(cmd).blocked


def test_editor_mode_commit_skips_validation():
    # no -m, no heredoc -> nothing to extract -> skip validation
    assert run("git commit").allowed


# ── INVOKE anchor: dangerous text inside string literals is not an invocation ─
def test_dangerous_inside_echo_allowed():
    # "git reset --hard" is an argument to echo, not an invocation
    assert run('echo "git reset --hard"').allowed


def test_no_verify_inside_echo_allowed():
    assert run('echo "git commit --no-verify"').allowed


# ── misc ──────────────────────────────────────────────────────────────────────
def test_empty_command_allowed():
    assert run("").allowed


def test_unrelated_command_allowed():
    assert run("ls -la").allowed
