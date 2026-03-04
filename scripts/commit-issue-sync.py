#!/usr/bin/env python3
"""PostToolUse hook: auto-detect issue refs in git commits and sync to GitHub.

Called by dispatcher.py when a Bash tool call contains 'git commit'.
Reads the commit message, extracts issue references (#N), and posts
a progress comment on the referenced issue.

Input: JSON on stdin with tool_input.command field
Output: JSON with status (always exits 0)
"""

import json
import re
import subprocess
import sys


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
    issue_numbers = set(re.findall(r"(?:Closes|Fixes|Refs|Part of|#)\s*#?(\d+)", commit_msg))

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
    repo = "JonesHong/workshop"
    for num in issue_numbers:
        comment = f"Commit `{commit_hash}`: {commit_msg.split(chr(10))[0]}"
        subprocess.run(
            ["gh", "issue", "comment", num, "--repo", repo, "--body", comment],
            capture_output=True,
        )

    json.dump(
        {
            "status": "synced",
            "issues": list(issue_numbers),
            "commit": commit_hash,
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
