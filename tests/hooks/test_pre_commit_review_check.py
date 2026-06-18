"""Tests for hooks/pre-commit-review-check.py — HARD BLOCK no reviewer since last successful commit.

Anchor: header comment. Detects whether a reviewer (Agent/Task with
subagent_type *containing* "general-purpose" + a GP_REVIEWER_PROMPTS filename in
the prompt) was invoked since the last *successful* git commit. Does not check
verdict. Failed commits do NOT count as window boundaries.
"""
from conftest import hook_stdin, make_transcript, run_hook

REVIEWER_PROMPT = "code-quality-reviewer-prompt.md"


def _review(tmp_path, events):
    tp = make_transcript(tmp_path, events)
    return run_hook(
        "pre-commit-review-check.py",
        hook_stdin("Bash", command='git commit -m "feat: x"', transcript_path=str(tp)),
    )


def test_blocks_source_edit_without_reviewer(tmp_path):
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
    ])
    assert res.blocked


def test_allows_source_edit_with_reviewer(tmp_path):
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
        {"role": "assistant", "tool": "Agent", "id": "u2",
         "input": {"subagent_type": "general-purpose", "prompt": f"use {REVIEWER_PROMPT} now"}},
    ])
    assert res.allowed


def test_non_source_edit_not_blocked(tmp_path):
    # tests/ path is exempt — no source change, no reviewer needed
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "tests/x.py"}},
    ])
    assert res.allowed


def test_no_edits_allowed(tmp_path):
    res = _review(tmp_path, [])
    assert res.allowed


def test_non_commit_command_allowed(tmp_path):
    tp = make_transcript(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
    ])
    res = run_hook(
        "pre-commit-review-check.py",
        hook_stdin("Bash", command="npm test", transcript_path=str(tp)),
    )
    assert res.allowed


def test_skip_review_check_override(tmp_path):
    tp = make_transcript(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
    ])
    res = run_hook(
        "pre-commit-review-check.py",
        hook_stdin("Bash", command='git commit -m "feat: x"', transcript_path=str(tp)),
        env={"SKIP_REVIEW_CHECK": "1"},
    )
    assert res.allowed


def test_missing_transcript_allowed(tmp_path):
    res = run_hook(
        "pre-commit-review-check.py",
        hook_stdin("Bash", command='git commit -m "feat: x"',
                   transcript_path=str(tmp_path / "nope.jsonl")),
    )
    assert res.allowed


def test_empty_transcript_path_allowed():
    res = run_hook(
        "pre-commit-review-check.py",
        hook_stdin("Bash", command='git commit -m "feat: x"'),
    )
    assert res.allowed


def test_window_boundary_successful_commit(tmp_path):
    # reviewer BEFORE a successful commit does not cover edits AFTER it
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Agent", "id": "u1",
         "input": {"subagent_type": "general-purpose", "prompt": REVIEWER_PROMPT}},
        {"role": "user", "id": "u1", "is_error": False},
        {"role": "assistant", "tool": "Bash", "id": "u2", "input": {"command": 'git commit -m "feat: first"'}},
        {"role": "user", "id": "u2", "is_error": False},  # successful -> window boundary
        {"role": "assistant", "tool": "Write", "id": "u3", "input": {"file_path": "src/b.py"}},
    ])
    assert res.blocked  # b.py edited after the commit, no reviewer since


def test_window_boundary_failed_commit_not_a_boundary(tmp_path):
    # reviewer BEFORE a FAILED commit still covers edits AFTER it — a failed
    # commit does not reset the window (otherwise a hook-blocked retry would
    # always fail)
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Agent", "id": "u1",
         "input": {"subagent_type": "general-purpose", "prompt": REVIEWER_PROMPT}},
        {"role": "user", "id": "u1", "is_error": False},
        {"role": "assistant", "tool": "Bash", "id": "u2", "input": {"command": 'git commit -m "feat: first"'}},
        {"role": "user", "id": "u2", "is_error": True},  # failed -> NOT a boundary
        {"role": "assistant", "tool": "Write", "id": "u3", "input": {"file_path": "src/b.py"}},
    ])
    assert res.allowed  # reviewer still in window (failed commit didn't reset)


def test_reviewer_subagent_type_case_insensitive(tmp_path):
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
        {"role": "assistant", "tool": "Agent", "id": "u2",
         "input": {"subagent_type": "General-Purpose", "prompt": REVIEWER_PROMPT}},
    ])
    assert res.allowed


def test_task_tool_name_counts_as_reviewer(tmp_path):
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
        {"role": "assistant", "tool": "Task", "id": "u2",
         "input": {"subagent_type": "general-purpose", "prompt": REVIEWER_PROMPT}},
    ])
    assert res.allowed


def test_reviewer_prompt_without_known_filename_not_counted(tmp_path):
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
        {"role": "assistant", "tool": "Agent", "id": "u2",
         "input": {"subagent_type": "general-purpose", "prompt": "please review this code"}},
    ])
    assert res.blocked


def test_non_general_purpose_subagent_not_counted(tmp_path):
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
        {"role": "assistant", "tool": "Agent", "id": "u2",
         "input": {"subagent_type": "code-reviewer", "prompt": REVIEWER_PROMPT}},
    ])
    assert res.blocked


def test_block_message_lists_files(tmp_path):
    res = _review(tmp_path, [
        {"role": "assistant", "tool": "Write", "id": "u1", "input": {"file_path": "src/a.py"}},
    ])
    assert res.has_block_msg("src/a.py")
