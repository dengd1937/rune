"""Tests for hooks/post-write-debug.sh — WARNS (never blocks) on debug statements."""
from conftest import hook_stdin, run_hook

import pytest

# (id, content, expect_warn)
DEBUG_CASES = [
    ("console-log", "console.log('x')", True),
    ("console-debug", "console.debug('x')", True),
    ("console-trace", "console.trace()", True),
    ("debugger-stmt", "if (x) { debugger; }", True),
    ("pdb-set-trace", "import pdb; pdb.set_trace()", True),
    ("import-pdb", "import pdb", True),
    ("breakpoint", "breakpoint()", True),
    ("plain-code", "const x = 1;", False),
    ("console-error-not-debug", "console.error('boom')", False),  # error is legit logging
]


@pytest.mark.parametrize(
    "content,expect_warn",
    [(c[1], c[2]) for c in DEBUG_CASES],
    ids=[c[0] for c in DEBUG_CASES],
)
def test_debug_detection(content, expect_warn):
    res = run_hook(
        "post-write-debug.sh",
        hook_stdin("Write", file_path="src/app.js", content=content),
    )
    assert res.allowed  # never blocks
    if expect_warn:
        assert res.warned, f"expected warning\n{res.stderr}"
    else:
        assert not res.warned, f"unexpected warning\n{res.stderr}"


def test_exempt_tests_path_no_warning():
    res = run_hook(
        "post-write-debug.sh",
        hook_stdin("Write", file_path="tests/debug.test.js", content="console.log('x')"),
    )
    assert not res.warned


def test_exempt_scripts_path_no_warning():
    res = run_hook(
        "post-write-debug.sh",
        hook_stdin("Write", file_path="scripts/setup.js", content="console.log('x')"),
    )
    assert not res.warned


def test_edit_new_string_checked():
    res = run_hook(
        "post-write-debug.sh",
        hook_stdin("Edit", file_path="src/app.js", new_string="console.log('x')"),
    )
    assert res.warned


def test_empty_content_no_warning():
    res = run_hook(
        "post-write-debug.sh",
        hook_stdin("Write", file_path="src/app.js", content=""),
    )
    assert not res.warned
