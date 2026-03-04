#!/usr/bin/env python3
"""session_context.py — Load open GitHub Issues into session context.

Called at session startup to inject current task state.
Output: Markdown summary of open issues for context injection.
"""

import json
import subprocess
import sys


def main():
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "open",
            "--json",
            "number,title,labels,createdAt",
            "--limit",
            "30",
        ],
        capture_output=True,
        text=True,
    )

    issues_raw = result.stdout.strip() if result.returncode == 0 else ""

    if not issues_raw or issues_raw == "[]":
        print("No open issues.")
        sys.exit(0)

    try:
        data = json.loads(issues_raw)
    except json.JSONDecodeError:
        print("No open issues.")
        sys.exit(0)

    if not data:
        print("No open issues.")
        sys.exit(0)

    in_progress = [i for i in data if any(l["name"] == "in-progress" for l in i.get("labels", []))]
    blocked = [i for i in data if any(l["name"] == "blocked" for l in i.get("labels", []))]
    in_progress_set = set(i["number"] for i in in_progress)
    blocked_set = set(i["number"] for i in blocked)
    ready = [
        i for i in data if i["number"] not in in_progress_set and i["number"] not in blocked_set
    ]

    print("## Open Issues")
    print()

    if in_progress:
        print("### In Progress")
        for issue in in_progress:
            labels = ", ".join(l["name"] for l in issue["labels"] if l["name"] != "in-progress")
            label_str = f" ({labels})" if labels else ""
            print(f"- #{issue['number']} {issue['title']}{label_str}")
        print()

    if blocked:
        print("### Blocked")
        for issue in blocked:
            print(f"- #{issue['number']} {issue['title']}")
        print()

    if ready:
        print("### Ready")
        for issue in ready[:10]:
            labels = ", ".join(l["name"] for l in issue["labels"])
            label_str = f" ({labels})" if labels else ""
            print(f"- #{issue['number']} {issue['title']}{label_str}")
        if len(ready) > 10:
            print(f"  ... and {len(ready) - 10} more")
        print()

    print(
        f"**Total**: {len(data)} open issues "
        f"({len(in_progress)} in-progress, {len(blocked)} blocked, {len(ready)} ready)"
    )


if __name__ == "__main__":
    main()
