"""Tests for hooks/pre-write-secrets.sh — BLOCKS writes containing secrets.

Anchor: header comment ("BLOCKS writes that contain secrets or private keys")
+ the PATTERNS array. Exempt paths (tests/, .env.example) are allowed.
"""
from conftest import hook_stdin, run_hook

import pytest

A32 = "a" * 32  # min length for sk- pattern

# (id, content, expect_block)
SECRET_CASES = [
    ("openai-key", f"api = 'sk-{A32}'", True),
    ("anthropic-ish-sk", "sk-" + "B" * 40, True),
    ("github-pat", "ghp_" + "c" * 36, True),
    ("github-oauth", "gho_" + "d" * 36, True),
    ("github-fine-grained", "github_pat_" + "e" * 40, True),
    ("aws-key-id", "AKIA" + "F" * 16, True),
    ("slack-bot", "xoxb-123-" + "g" * 10, True),
    ("slack-user", "xoxp-123-" + "h" * 10, True),
    ("google-api", "AIza" + "J" * 35, True),
    ("rsa-private-key", "-----BEGIN RSA PRIVATE KEY-----", True),
    ("ec-private-key", "-----BEGIN EC PRIVATE KEY-----", True),
    ("openssh-private-key", "-----BEGIN OPENSSH PRIVATE KEY-----", True),
    ("bare-private-key", "-----BEGIN PRIVATE KEY-----", True),
    ("plain-code", "const x = 1;", False),
    ("sk-too-short", "sk-abc", False),  # needs 32+ chars after sk-
    ("random-text", "hello world", False),
]


@pytest.mark.parametrize(
    "content,expect_block", [(c[1], c[2]) for c in SECRET_CASES], ids=[c[0] for c in SECRET_CASES]
)
def test_secret_detection(content, expect_block):
    res = run_hook(
        "pre-write-secrets.sh",
        hook_stdin("Write", file_path="src/config.js", content=content),
    )
    if expect_block:
        assert res.blocked, f"expected block\n{res.stderr}"
    else:
        assert res.allowed, f"expected allow\n{res.stderr}"


def test_exempt_tests_dir_allows_secret():
    res = run_hook(
        "pre-write-secrets.sh",
        hook_stdin("Write", file_path="tests/fixtures/config.js", content=f"sk-{A32}"),
    )
    assert res.allowed


def test_exempt_env_example_allows_secret():
    res = run_hook(
        "pre-write-secrets.sh",
        hook_stdin("Write", file_path=".env.example", content=f"OPENAI_KEY=sk-{A32}"),
    )
    assert res.allowed


def test_empty_content_allowed():
    res = run_hook(
        "pre-write-secrets.sh",
        hook_stdin("Write", file_path="src/x.js", content=""),
    )
    assert res.allowed


def test_edit_new_string_is_checked():
    # Edit tool exposes the change as new_string, not content.
    res = run_hook(
        "pre-write-secrets.sh",
        hook_stdin("Edit", file_path="src/x.js", new_string="ghp_" + "c" * 36),
    )
    assert res.blocked


def test_block_message_names_file():
    res = run_hook(
        "pre-write-secrets.sh",
        hook_stdin("Write", file_path="src/leak.js", content=f"sk-{A32}"),
    )
    assert res.has_block_msg("src/leak.js")
