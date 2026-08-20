#!/usr/bin/env python3
"""PostToolUse hook: auto-detect issue refs in git commits and sync to GitHub.

Called by dispatcher.py when a Bash tool call contains 'git commit'.
Reads the commit message, extracts issue references (#N), and posts
a progress comment on the referenced issue.

Input: JSON on stdin with tool_input.command field
Output: JSON with status (always exits 0)
"""

import json
import os
import re
import sqlite3
import subprocess
import sys


def _repo_from_git_remote() -> str:
    """Derive owner/repo from the current checkout's origin.

    The repo used to be hardcoded, which meant anyone running this pointed it at
    someone else's project. Set GITHUB_PM_REPO to override; otherwise this reads
    whatever checkout you are standing in.
    """
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        raise SystemExit(
            "Cannot determine the target repo: set GITHUB_PM_REPO, "
            "or run this from a checkout that has an origin remote."
        )
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    if not m:
        raise SystemExit(f"Could not parse owner/repo out of origin url: {url}")
    return m.group(1)


def should_post(issue, commit_hash, db_path):
    """Return True the first time (issue, commit_hash) is seen, False after.

    Records the pair in a SQLite dedup table. Re-triggered hooks (rebase /
    amend / hook replay) on the same commit then skip re-commenting.
    """
    # ponytail: keyed on git short hash; if we switch to squash-merge the
    # hash drifts, so re-key on (issue, first-line) when that happens.
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS comment_dedup "
            "(issue TEXT, commit_hash TEXT, UNIQUE(issue, commit_hash))"
        )
        cursor = conn.execute(
            "INSERT OR IGNORE INTO comment_dedup (issue, commit_hash) VALUES (?, ?)",
            (issue, commit_hash),
        )
        conn.commit()
        return cursor.rowcount != 0
    finally:
        conn.close()


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        json.dump({"status": "skip", "reason": "no input"}, sys.stdout)
        return

    command = data.get("tool_input", {}).get("command", "")

    # Only trigger on git commit commands
    if "git commit" not in command:
        json.dump({"status": "skip"}, sys.stdout)
        return

    # Get the latest commit message
    result = subprocess.run(
        ["git", "log", "-1", "--format=%s%n%b"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        json.dump({"status": "skip", "reason": "git log failed"}, sys.stdout)
        return

    commit_msg = result.stdout.strip()
    commit_hash = subprocess.run(
        ["git", "log", "-1", "--format=%h"],
        capture_output=True,
        text=True,
    ).stdout.strip()

    # Extract issue references (#N, Refs #N, Closes #N, Fixes #N)
    issue_numbers = set(
        re.findall(r"(?:Closes|Fixes|Refs|Part of|#)\s*#?(\d+)", commit_msg)
    )

    # Also check branch name for issue reference
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    branch_issue = re.search(r"#(\d+)", branch)
    if branch_issue:
        issue_numbers.add(branch_issue.group(1))

    if not issue_numbers:
        json.dump({"status": "skip", "reason": "no issue refs"}, sys.stdout)
        return

    # Post comment on each referenced issue
    repo = os.environ.get("GITHUB_PM_REPO") or _repo_from_git_remote()
    db_path = os.path.expanduser("~/.claude/data/github-pm/comment_dedup.db")
    posted = []
    for num in issue_numbers:
        if not should_post(num, commit_hash, db_path):
            continue
        comment = f"Commit `{commit_hash}`: {commit_msg.split(chr(10))[0]}"
        subprocess.run(
            ["gh", "issue", "comment", num, "--repo", repo, "--body", comment],
            capture_output=True,
        )
        posted.append(num)

    json.dump(
        {
            "status": "synced",
            "issues": posted,
            "commit": commit_hash,
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
