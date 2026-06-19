#!/usr/bin/env python3
"""Tests for should_post dedup logic in commit-issue-sync.py.

Pure unit tests: only exercise the SQLite dedup state. Never call gh /
GitHub. Run: ~/.local/bin/python3 scripts/test_comment_dedup.py
"""

import importlib.util
import os
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "commit_issue_sync", os.path.join(_HERE, "commit-issue-sync.py")
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
should_post = _mod.should_post


def test_dedup_same_issue_commit():
    tmp = tempfile.mkdtemp()
    db = os.path.join(tmp, "nested", "comment_dedup.db")
    first = should_post("42", "abc1234", db)
    second = should_post("42", "abc1234", db)
    assert first is True, "first call should post"
    assert second is False, "second call (same issue+hash) should skip"


def test_dedup_distinguishes_pairs():
    tmp = tempfile.mkdtemp()
    db = os.path.join(tmp, "comment_dedup.db")
    assert should_post("1", "deadbee", db) is True
    assert should_post("2", "deadbee", db) is True  # diff issue, same hash
    assert should_post("1", "cafef00", db) is True  # same issue, diff hash
    assert should_post("1", "deadbee", db) is False  # repeat of first


def run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print("OK", len(tests), "tests")


if __name__ == "__main__":
    run()
