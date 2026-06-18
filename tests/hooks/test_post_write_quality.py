"""Tests for hooks/post-write-quality.sh — WARNS on file size + language anti-patterns.

PostToolUse runs after the tool, so the file must exist on disk; size checks read
the real file (`wc -l`), anti-pattern checks read the json content/new_string.
"""
from conftest import hook_stdin, run_hook


def _write_file(tmp_path, name, lines):
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(["x"] * lines) + "\n")
    return str(p)


def test_size_over_max_warning(tmp_path):
    f = _write_file(tmp_path, "big.ts", 801)
    res = run_hook("post-write-quality.sh", hook_stdin("Write", file_path=f, content="x"))
    assert res.allowed
    assert res.has_warning("800")


def test_size_soft_warning(tmp_path):
    f = _write_file(tmp_path, "mid.ts", 401)
    res = run_hook("post-write-quality.sh", hook_stdin("Write", file_path=f, content="x"))
    assert res.has_warning("400")


def test_size_ok_no_warning(tmp_path):
    f = _write_file(tmp_path, "small.ts", 100)
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Write", file_path=f, content="const x = 1;"),
    )
    assert not res.warned


def test_ts_any_warning(tmp_path):
    f = _write_file(tmp_path, "a.ts", 5)
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Write", file_path=f, content="const x: any = 1;"),
    )
    assert res.has_warning("any")


def test_ts_react_fc_warning(tmp_path):
    f = _write_file(tmp_path, "b.tsx", 5)
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Write", file_path=f, content="const C: React.FC = () => null;"),
    )
    assert res.has_warning("React.FC")


def test_python_environ_get_warning(tmp_path):
    f = _write_file(tmp_path, "a.py", 5)
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Write", file_path=f, content="x = os.environ.get('K')"),
    )
    assert res.has_warning("os.environ")


def test_python_mutable_default_list(tmp_path):
    f = _write_file(tmp_path, "b.py", 5)
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Write", file_path=f, content="def f(x=[]): pass"),
    )
    assert res.has_warning("mutable")


def test_python_mutable_default_dict(tmp_path):
    f = _write_file(tmp_path, "c.py", 5)
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Write", file_path=f, content="def f(x={}): pass"),
    )
    assert res.has_warning("mutable")


def test_exempt_path_no_warning(tmp_path):
    f = _write_file(tmp_path, "tests/x.ts", 900)
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Write", file_path=f, content="const x: any = 1;"),
    )
    assert not res.warned


def test_missing_file_no_warning(tmp_path):
    # PostToolUse expects the file on disk; absent file -> exit 0, no warning.
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Write", file_path=str(tmp_path / "nope.ts"), content="const x: any = 1;"),
    )
    assert not res.warned


def test_edit_checks_new_string_not_size(tmp_path):
    # Edit mode reads only new_string anti-patterns, not file size.
    f = _write_file(tmp_path, "big.ts", 900)
    res = run_hook(
        "post-write-quality.sh",
        hook_stdin("Edit", file_path=f, new_string="const x: any = 1;"),
    )
    assert res.has_warning("any")
    assert "800" not in res.stderr
