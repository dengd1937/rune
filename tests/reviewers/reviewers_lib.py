"""Deterministic harness logic for the B-layer reviewer tests.

The behavioral runner (`run-reviewer-test.sh`) has five stages; three of them
(build system prompt, build user message, verdict) are pure string functions
with zero LLM dependency. They used to live as embedded `python3 -c` / `awk`
inside a single-quoted bash string — unreadable, untestable, and fragile (any
apostrophe in a comment closed the bash string and broke the script; that bit
us twice). They are extracted here so:

  - they are importable and unit-tested by `test_verdict_logic.py` ($0, ms, CI),
  - the verdict/extract conclusion logic — where three real bugs once hid,
    each costing a full LLM run to find — is regression-locked,
  - the regex-vocab defaults have a single source of truth (not duplicated in
    bash), and
  - the bash runner is a thin orchestrator over this module's CLI.

Named `reviewers_lib.py` (not `conftest.py`): two files named conftest.py across
tests/hooks and tests/skills collide under pytest's prepend import mode, so each
test layer uses a distinctly-named helper module (cf. tests/skills/skills_lib.py).
"""
from __future__ import annotations

import argparse
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

# ── single source of truth for verdict vocabulary ────────────────────────────
# Broad on purpose so positive verdict assertions hold across real reviewer
# phrasings (EN + ZH). Override per-scenario via the CLI flags / decide() kwargs.
DEFAULT_EXPECT = "block"
DEFAULT_SEVERITY_RE = r"critical|high|严重|高危|严重风险"
DEFAULT_APPROVE_RE = (
    r"approve|approved|规格合规|批准|looks good|lgtm|no issues|没问题|可合并|ready to merge"
)
DEFAULT_BLOCK_RE = (
    # Hard verdicts only — soft phrasings ("request changes" / "建议修改") are
    # advice, not a block, and false-blocked clean code in the approve direction.
    r"block|reject|拒绝|must fix|必须修复|do not merge|不能合并|"
    r"不批准|不合规|不通过|未通过"
)

# Conclusion marker: the verdict rides after the LAST line matching this.
# Tolerates markdown bold ("**Status:**") — an earlier `Status:\s*[A-Za-z]`
# marker missed the bold form and silently dropped tech-risk/plan conclusions.
_CONCLUSION_MARKER = re.compile(r"结论|Status\s*:")
# Fenced code blocks, used to segment a prompt template without cross-fence
# bridging (an earlier `.*?`-with-DOTALL regex bridged across fences).
_FENCE_RE = re.compile(r"```[a-zA-Z]*\n(.*?)\n```", re.S)
_WRAPPER_PROMPT_RE = re.compile(r"prompt:\s*\|")
_LEAK_RE = re.compile(r"\{\{[A-Z_]+\}\}|\[[A-Z][A-Z_]*_[A-Z_]+\]")


# ── stage ②: build the reviewer system prompt from a template ────────────────
def build_system_prompt(
    template_text: str,
    *,
    task_text: str = "",
    plan_text: str = "",
    task_summaries: str = "",
    implementer_report: str = "",
    ratified_decisions: str = "",
    spec_text: str = "(no spec provided)",
    base_sha: str = "abc1234",
    head_sha: str = "def5678",
) -> str:
    """Extract the real prompt from a template and substitute placeholders.

    writing-plans templates wrap the prompt in a ```code fence under `prompt: |`
    -> extract + dedent that. code-review/design templates are inline prose with
    no such fence -> use the whole file. Then substitute every placeholder
    (both {{X}} and [X] styles); {{DIFF}}/{{PLAN_FILE_PATH}} point at the user
    message (the fixture rides there).
    """
    fences = _FENCE_RE.findall(template_text)
    wrapper = next((f for f in fences if _WRAPPER_PROMPT_RE.search(f)), None)
    if wrapper:
        m = re.search(r"prompt:\s*\|\s*\n(.*)", wrapper, re.S)
        text = textwrap.dedent(m.group(1))
    else:
        text = template_text
    in_user_msg = "(the diff/plan is in the user message below)"
    subs = {
        "{{TASK_TEXT}}": task_text,
        "{{PLAN_TEXT}}": plan_text,
        "{{TASK_SUMMARIES}}": task_summaries,
        "{{IMPLEMENTER_REPORT}}": implementer_report,
        "{{RATIFIED_DECISIONS}}": ratified_decisions,
        "{{DIFF}}": in_user_msg,
        "{{BASE_SHA}}": base_sha,
        "{{HEAD_SHA}}": head_sha,
        "{{PLAN_FILE_PATH}}": in_user_msg,
        "{{SPEC_FILE_PATH}}": spec_text,
        "[PLAN_FILE_PATH]": in_user_msg,
        "[SPEC_FILE_PATH]": spec_text,
    }
    for k, v in subs.items():
        text = text.replace(k, v)
    return text


def find_unsubstituted(text: str) -> list[str]:
    """Placeholders a template grew that the runner does not substitute.

    Bracket style requires an underscore so legit tokens like [CRITICAL]/[HIGH]
    in severity tables are not flagged.
    """
    return _LEAK_RE.findall(text)


# ── stage ③: build the user message (fixture + trigger) ──────────────────────
def build_user_message(fixture_content: str, *, context: str = "", lang: str = "diff") -> str:
    parts: list[str] = []
    if context:
        parts.append(context + "\n")
    parts.append(f"```{lang}\n{fixture_content}\n```\n")
    parts.append("请按你的审查流程审查上述内容，输出完整审查结果与结论。")
    return "\n".join(parts)


# ── stage ⑤: extract the conclusion + decide the verdict ─────────────────────
def extract_conclusion(output: str) -> str:
    """Text after the LAST 结论/Status: marker line. Empty if no marker."""
    lines = output.splitlines()
    last = None
    for i, line in enumerate(lines):
        if _CONCLUSION_MARKER.search(line):
            last = i
    if last is None:
        return ""
    return "\n".join(lines[last:])


def _all_marked_sections(output: str) -> str:
    """Text from the FIRST 结论/Status: marker to end.

    Tier 2 of the conclusion fallback: a reviewer sometimes splits its verdict
    across sections, with the LAST marker section holding only notes and the
    actual APPROVE/BLOCK living in an EARLIER section. Scanning from the first
    marker recovers it. Empty if no marker at all.
    """
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if _CONCLUSION_MARKER.search(line):
            return "\n".join(lines[i:])
    return ""


def _conclusion_or_fallback(
    output: str, *, verdict_re: str = "", fallback_lines: int = 6
) -> str:
    """Three-tier conclusion extraction.

      1. Text after the LAST 结论/Status: marker (keeps the verdict out of the
         body, so reasoning like "no SQL injection" is not misread as one).
      2. If (1) is non-empty but carries no verdict word (approve|block), the
         verdict may sit in an earlier section -> take all text from the FIRST
         marker onward.
      3. No marker at all -> the last N non-blank lines.
    """
    concl = extract_conclusion(output)
    if concl.strip() and verdict_re and not _has(verdict_re, concl):
        all_marked = _all_marked_sections(output)
        if all_marked.strip():
            return all_marked
    if concl.strip():
        return concl
    nonblank = [ln for ln in output.splitlines() if ln.strip()]
    return "\n".join(nonblank[-fallback_lines:])


@dataclass
class Verdict:
    expect: str
    passed: bool
    lines: list[str] = field(default_factory=list)


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


def decide(
    output: str,
    *,
    expect: str,
    bug_re: str,
    severity_re: str = DEFAULT_SEVERITY_RE,
    approve_re: str = DEFAULT_APPROVE_RE,
    block_re: str = DEFAULT_BLOCK_RE,
) -> Verdict:
    """Evaluate a reviewer's output against the expected direction.

    - expect="block"  (planted bug): must flag the bug (whole output), signal
      severity (whole output), and explicitly BLOCK (conclusion only). Positive
      BLOCK assertion — a rubber-stamper that never blocks fails here.
    - expect="approve" (clean control): must APPROVE and NOT block (conclusion).

    bug/severity scan the full output (the bug discussion lives in the body);
    approve/block scan only the conclusion, so body reasoning like
    "no SQL injection" / "no must-fix issues" / "No blocking issues found"
    is not misread as a verdict.
    """
    conclusion = _conclusion_or_fallback(output, verdict_re=f"{approve_re}|{block_re}")
    has_bug = _has(bug_re, output)
    has_sev = _has(severity_re, output)
    has_approve = _has(approve_re, conclusion)
    has_block = _has(block_re, conclusion)
    lines: list[str] = []

    if expect == "approve":
        lines.append(_line(has_approve, "approved", "did not approve a clean fixture", approve_re))
        lines.append(_line(not has_block, "not blocked", "blocked a clean fixture — over-blocking", block_re))
        passed = has_approve and not has_block
    else:
        lines.append(_line(has_bug, "bug flagged", "bug missed", bug_re))
        lines.append(_line(has_sev, "severity signal", "no severity signal", severity_re))
        lines.append(_line(has_block, "blocked (explicit)", "did not explicitly block — sycophantic", block_re))
        passed = has_bug and has_sev and has_block

    return Verdict(expect=expect, passed=passed, lines=lines)


def _line(ok: bool, pass_msg: str, fail_msg: str, detail: str) -> str:
    tag = "PASS" if ok else "FAIL"
    msg = pass_msg if ok else f"{fail_msg} ({detail})"
    return f"  [{tag}] {msg}"


# ── CLI: thin wrapper so the bash runner stays a thin orchestrator ────────────
def _cli() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("build-system-prompt")
    sp.add_argument("--template", required=True)
    sp.add_argument("--out", required=True)
    sp.add_argument("--task-text", default="")
    sp.add_argument("--plan-text", default="")
    sp.add_argument("--task-summaries", default="")
    sp.add_argument("--implementer-report", default="")
    sp.add_argument("--ratified-decisions", default="")
    sp.add_argument("--spec-text", default="(no spec provided)")
    sp.add_argument("--base-sha", default="abc1234")
    sp.add_argument("--head-sha", default="def5678")

    um = sub.add_parser("build-user-message")
    um.add_argument("--fixture", required=True)
    um.add_argument("--out", required=True)
    um.add_argument("--context", default="")
    um.add_argument("--lang", default="diff")

    de = sub.add_parser("decide")
    de.add_argument("--output-file", required=True)
    de.add_argument("--expect", default=DEFAULT_EXPECT)
    de.add_argument("--bug-re", required=True)
    de.add_argument("--severity-re", default=DEFAULT_SEVERITY_RE)
    de.add_argument("--approve-re", default=DEFAULT_APPROVE_RE)
    de.add_argument("--block-re", default=DEFAULT_BLOCK_RE)

    args = p.parse_args()

    if args.cmd == "build-system-prompt":
        tpl = Path(args.template).read_text(encoding="utf-8")
        text = build_system_prompt(
            tpl,
            task_text=args.task_text,
            plan_text=args.plan_text,
            task_summaries=args.task_summaries,
            implementer_report=args.implementer_report,
            ratified_decisions=args.ratified_decisions,
            spec_text=args.spec_text,
            base_sha=args.base_sha,
            head_sha=args.head_sha,
        )
        leaks = find_unsubstituted(text)
        if leaks:
            print(f"[warn] unsubstituted placeholders in system prompt: {leaks}", file=sys.stderr)
        Path(args.out).write_text(text, encoding="utf-8")
        return 0

    if args.cmd == "build-user-message":
        content = Path(args.fixture).read_text(encoding="utf-8")
        Path(args.out).write_text(
            build_user_message(content, context=args.context, lang=args.lang), encoding="utf-8"
        )
        return 0

    if args.cmd == "decide":
        output = Path(args.output_file).read_text(encoding="utf-8")
        v = decide(
            output,
            expect=args.expect,
            bug_re=args.bug_re,
            severity_re=args.severity_re,
            approve_re=args.approve_re,
            block_re=args.block_re,
        )
        for ln in v.lines:
            print(ln)
        return 0 if v.passed else 1

    return 2  # unreachable (argparse required=True)


if __name__ == "__main__":
    sys.exit(_cli())
