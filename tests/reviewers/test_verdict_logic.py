"""Unit tests for the B-layer harness logic (reviewers_lib).

These are the deterministic, zero-LLM stages of `run-reviewer-test.sh` (build
system prompt, extract conclusion, decide verdict). They are regression locks
for three real bugs that each cost a full LLM run to find:

  1. APPROVE bare `合规`/`通过` substring-matched `不合规`/`不通过` (false approve).
  2. The conclusion marker missed markdown `**Status:**` (conclusion dropped).
  3. A BLOCK regex `issues found` matched the negation "No ... issues found".

And for the output-FORMAT coupling: if a reviewer prompt's conclusion shape
changes, the relevant case here fails loudly — before any LLM run.
"""
from __future__ import annotations

import pytest

from reviewers_lib import (
    DEFAULT_APPROVE_RE,
    DEFAULT_BLOCK_RE,
    DEFAULT_SEVERITY_RE,
    build_system_prompt,
    build_user_message,
    decide,
    extract_conclusion,
    find_unsubstituted,
)

APR = DEFAULT_APPROVE_RE
BLK = DEFAULT_BLOCK_RE
SEV = DEFAULT_SEVERITY_RE


# ── decide(): verdict direction + the 3 bug classes + format coupling ─────────

# (id, output, expect, extra-regex-kwargs, expected_passed)
DECIDE_CASES = [
    # bug-class 1: body negations must NOT read as a block (whole-output grep
    # originally false-blocked here). Clean approve conclusion.
    (
        "body-negations-approve",
        "Reviewed. No SQL injection, no hardcoded secrets, no must-fix issues.\n"
        "### 结论\n- **APPROVE**：无 CRITICAL/HIGH 问题",
        "approve", {}, True,
    ),
    # baseline block: bug + severity in body, explicit BLOCK in conclusion.
    (
        "block-baseline",
        "SQL injection via string concat — CRITICAL.\n### 结论\n- **BLOCK**：必须修复",
        "block", {"bug_re": "injection|注入"}, True,
    ),
    # bug-class 2: markdown-bold **Status:** must be captured as a conclusion
    # marker (the old `Status:\s*[A-Za-z]` missed the bold form).
    (
        "markdown-bold-status-block",
        "Found injection — CRITICAL.\n**Status:** Block",
        "block", {"bug_re": "injection", "severity_re": SEV}, True,
    ),
    # bug-class 3: "No blocking issues found" must NOT trip a BLOCK regex.
    # Uses the plan-clean override `\*\* issues found` (anchored to the status).
    (
        "plan-clean-no-issues-found-trap",
        "**Status:** Approved\nThe plan is complete.\nNo blocking issues found.",
        "approve", {"block_re": r"\*\* issues found"}, True,
    ),
    # plan buggy: status "Issues Found" IS caught by the anchored block regex.
    # (plan/tech-risk use a different severity vocab than code reviewers —
    #  "Issues Found"/缺陷/问题 IS the severity signal there.)
    (
        "plan-buggy-issues-found",
        "Placeholders and TODOs present.\n**Status:** Issues Found",
        "block",
        {"bug_re": "todo|placeholder", "severity_re": "issues found|缺陷|问题|placeholder|todo",
         "block_re": r"\*\* issues found|issues found"},
        True,
    ),
    # bug-class 1 (the substring trap): approve `规格合规` is NOT a substring of
    # block `不合规`; block output must not be read as approved, and vice versa.
    (
        "spec-block-buhegui-not-approved",
        "Missing required prop.\n### 结论\n- ❌ **不合规**",
        "approve", {"approve_re": r"规格合规", "block_re": r"不合规|不通过"}, False,
    ),
    (
        "spec-approve-guigehegui",
        "All required props implemented.\n### 结论\n- ✅ **规格合规**",
        "approve", {"approve_re": r"规格合规", "block_re": r"不合规|不通过"}, True,
    ),
    # tech-risk vocab path: Needs-Attention status.
    (
        "techrisk-needs-attention-overblock",
        "No Repository layer; perf risk.\n**Status:** Needs-Attention",
        "approve", {"block_re": r"needs-attention|needs attention"}, False,
    ),
    # fallback path: no 结论/Status: marker -> conclusion = last non-blank lines.
    (
        "no-marker-fallback-approve",
        "Short review.\nLooks good — ready to merge.",
        "approve", {}, True,
    ),
    # empty output / claude error -> safe failure (no false pass).
    ("empty-output-block-fails", "", "block", {"bug_re": "x"}, False),
    ("empty-output-approve-fails", "", "approve", {}, False),
    # sycophancy guard: planted bug but reviewer rubber-stamps with no block word.
    (
        "sycophant-no-block",
        "There is a SQL injection here.\n### 结论\n- **APPROVE**：looks good, no issues",
        "block", {"bug_re": "injection"}, False,
    ),
    # body vs conclusion scoping: "approved" mentioned in BODY must not count as
    # the verdict (the verdict scans the conclusion only).
    (
        "approve-word-in-body-not-verdict",
        "The previous version was approved.\n### 结论\n- **BLOCK**：regression found",
        "approve", {}, False,
    ),
    # three-tier extraction: the LAST 结论 section holds only notes (no verdict
    # word), but the actual BLOCK is in an EARLIER 结论 section. The single-tier
    # extractor dropped it; tier 2 scans from the FIRST marker and recovers it.
    (
        "verdict-in-earlier-section-block",
        "### 结论\n- **BLOCK**：SQL injection is critical — must fix\n\n"
        "## 附注\n### 结论\n- 已记录，无补充",
        "block", {"bug_re": "injection", "severity_re": SEV}, True,
    ),
    # bug-class (tighten): soft phrasings ("request changes" / "建议修改") are
    # advice, not a hard BLOCK. The broad BLOCK regex false-blocked clean code;
    # the tightened default excludes them so an APPROVE-with-minor-suggestion
    # is not over-blocked.
    (
        "soft-phrasing-not-a-block-approve",
        "Reviewed the clean diff.\n### 结论\n- **APPROVE**：代码良好，仅建议修改命名风格",
        "approve", {}, True,
    ),
]


@pytest.mark.parametrize(
    "output, expect, kw, passed",
    [(c[1], c[2], c[3], c[4]) for c in DECIDE_CASES],
    ids=[c[0] for c in DECIDE_CASES],
)
def test_decide(output, expect, kw, passed):
    assert decide(output, expect=expect, bug_re=kw.pop("bug_re", "injection"), **kw).passed is passed


# ── extract_conclusion(): marker + fallback mechanics ─────────────────────────

def test_extract_conclusion_last_marker_wins():
    out = "Status: draft notes\n...body...\n### 结论\n- **BLOCK**"
    assert "BLOCK" in extract_conclusion(out)
    # an earlier Status: line must not win over the later 结论 marker
    assert "draft notes" not in extract_conclusion(out)


def test_extract_conclusion_no_marker_empty():
    assert extract_conclusion("just a review\nwith no verdict marker") == ""


# ── build_system_prompt(): extraction + substitution + leak guard ─────────────

PROSE_TEMPLATE = (
    "# Reviewer\n\nYou review code.\n\n## Task\n{{TASK_TEXT}}\n\n"
    "```diff\n{{DIFF}}\n```\n\nBASE: {{BASE_SHA}}\n"
)

WRAPPER_TEMPLATE = (
    "Intro prose.\n\n```\nTask tool (general-purpose):\n  prompt: |\n"
    "    You are a plan reviewer.\n\n    **Plan:** [PLAN_FILE_PATH]\n```\n"
)


def test_build_system_prompt_prose_uses_whole_file():
    out = build_system_prompt(PROSE_TEMPLATE, task_text="do the thing", base_sha="aaa", head_sha="bbb")
    assert "do the thing" in out
    assert "aaa" in out
    # {{DIFF}} -> pointer to user message
    assert "{{DIFF}}" not in out
    assert "user message" in out


def test_build_system_prompt_wrapper_extracted_and_dedented():
    out = build_system_prompt(WRAPPER_TEMPLATE)
    # the Task-tool header is NOT part of the extracted prompt
    assert "Task tool" not in out
    assert "You are a plan reviewer." in out
    # [PLAN_FILE_PATH] substituted to the user-message pointer
    assert "[PLAN_FILE_PATH]" not in out
    assert "user message" in out


def test_build_system_prompt_no_cross_fence_bridging():
    # A prose template whose ```diff``` example fence happens to contain the
    # word "prompt:" must NOT be mis-extracted as a Task-tool wrapper.
    tpl = "# R\n\n```diff\n{{DIFF}}\n```\n\nNote: see prompt: above.\n\n{{TASK_TEXT}}\n"
    out = build_system_prompt(tpl, task_text="T")
    assert "Note: see prompt: above" in out  # whole-file path kept the note
    assert "T" in out


def test_find_unsubstituted_flags_new_placeholder():
    text = "kept {{TASK_TEXT}} but leaked {{NEW_VAR}} and [SOME_PATH]"
    leaks = find_unsubstituted(text)
    assert "{{NEW_VAR}}" in leaks
    assert "[SOME_PATH]" in leaks


def test_find_unsubstituted_ignores_severity_tokens():
    # [CRITICAL]/[HIGH] are legit severity-table tokens, not placeholders
    # (bracket style requires an underscore).
    assert find_unsubstituted("[CRITICAL] issue [HIGH] note {{OK}}") == ["{{OK}}"]


# ── build_user_message ────────────────────────────────────────────────────────

def test_build_user_message_wraps_fixture_with_trigger():
    msg = build_user_message("diff --git a/x b/x\n+hello\n", lang="diff")
    assert "```diff\n" in msg
    assert "+hello" in msg
    assert "审查" in msg  # Chinese trigger sentence


def test_build_user_message_optional_context_prepended():
    msg = build_user_message("content", context="PRIOR CONTEXT", lang="markdown")
    assert msg.startswith("PRIOR CONTEXT\n")
