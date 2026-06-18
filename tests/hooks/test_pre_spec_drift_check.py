"""Tests for hooks/pre-spec-drift-check.sh — ADVISORY (exit 0) spec-drift warning.

Anchor: header comment. Warns (non-blocking) when a commit touches code in a
module that has a capability spec (per docs/CODEMAP.md) but neither that spec
nor a changes/*/specs.md delta is touched. Bypass: non-behavior commit types
+ the [no-spec-change] token. No-op without docs/CODEMAP.md (e.g. Rune itself).
"""
import subprocess

from conftest import hook_stdin, run_hook, write_codemap


def _stage(repo, path, content="x = 1\n"):
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    subprocess.run(["git", "add", path], cwd=repo, check=True)


def _run(repo, message):
    return run_hook(
        "pre-spec-drift-check.sh",
        hook_stdin("Bash", command=f'git commit -m "{message}"'),
        cwd=repo,
    )


def test_no_codemap_is_noop(tmp_repo):
    _stage(tmp_repo, "src/x.py")
    res = _run(tmp_repo, "feat: x")
    assert res.allowed and not res.warned


def test_drift_warns_when_spec_not_touched(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "src/auth/login.py")
    res = _run(tmp_repo, "feat: x")
    assert res.allowed  # advisory, never blocks
    assert res.has_warning("spec drift")


def test_no_warning_when_spec_also_touched(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "src/auth/login.py")
    _stage(tmp_repo, "docs/specs/auth-spec.md", "# auth spec\n")
    res = _run(tmp_repo, "feat: x")
    assert not res.warned


def test_no_warning_when_delta_covers_capability(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "src/auth/login.py")
    delta = tmp_repo / "docs/changes/feat-1/specs.md"
    delta.parent.mkdir(parents=True, exist_ok=True)
    delta.write_text("## auth\n- some delta\n", encoding="utf-8")
    subprocess.run(["git", "add", "docs/changes/feat-1/specs.md"], cwd=tmp_repo, check=True)
    res = _run(tmp_repo, "feat: x")
    assert not res.warned


def test_bypass_non_behavior_types(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "src/auth/login.py")
    for msg in ["refactor: x", "docs: x", "chore: x", "test: x", "ci: x", "perf: x"]:
        res = _run(tmp_repo, msg)
        assert not res.warned, f"{msg} should bypass"


def test_bypass_no_spec_change_token(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "src/auth/login.py")
    res = _run(tmp_repo, "feat: x [no-spec-change]")
    assert not res.warned


def test_docs_path_does_not_trigger(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "docs/random.md", "# notes\n")
    res = _run(tmp_repo, "feat: x")
    assert not res.warned


def test_module_not_in_codemap_no_warning(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "src/other/x.py")  # different module, not specced
    res = _run(tmp_repo, "feat: x")
    assert not res.warned


def test_no_specced_modules_is_noop(tmp_repo):
    write_codemap(tmp_repo, [("src/x.py", None)])  # cap='-' -> no spec
    _stage(tmp_repo, "src/x.py")
    res = _run(tmp_repo, "feat: x")
    assert not res.warned


def test_editor_mode_commit_no_warning(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "src/auth/login.py")
    res = run_hook(
        "pre-spec-drift-check.sh",
        hook_stdin("Bash", command="git commit"),  # no -m
        cwd=tmp_repo,
    )
    assert not res.warned


def test_non_commit_command_no_warning(tmp_repo):
    write_codemap(tmp_repo, [("src/auth/login.py", "auth")])
    _stage(tmp_repo, "src/auth/login.py")
    res = run_hook(
        "pre-spec-drift-check.sh",
        hook_stdin("Bash", command="npm test"),
        cwd=tmp_repo,
    )
    assert not res.warned
