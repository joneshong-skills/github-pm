#!/usr/bin/env python3
"""Parse a blueprint .md file and create GitHub Issues from its phases/tasks.

Usage: python3 blueprint-to-issues.py <blueprint-path> [--dry-run]

Blueprint format (from our blueprint skill):
- Has ## Phase N: ... sections
- Each phase has ### Task N.M: ... subsections
- Tasks have bullet points for details and acceptance criteria

The script:
1. Parses the blueprint markdown
2. Creates an Epic issue (the overall blueprint)
3. Creates Task issues for each phase/task
4. Links tasks to epic via "Part of #N" in body
5. Adds dependency info ("Depends on #N") based on phase ordering
6. Applies labels based on content detection (backend/frontend/infra)
7. Outputs a summary table
"""

import os
import re
import subprocess
import sys
from pathlib import Path


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

REPO = os.environ.get("GITHUB_PM_REPO") or _repo_from_git_remote()


def run_gh(args: list[str]) -> str:
    """Run gh CLI command and return output."""
    result = subprocess.run(["gh", *args, "--repo", REPO], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"gh error: {result.stderr}", file=sys.stderr)
    return result.stdout.strip()


def ensure_labels():
    """Create standard labels if they don't exist."""
    labels = {
        "epic": "7C3AED",
        "feature": "1D76DB",
        "bug": "D73A4A",
        "backend": "0E8A16",
        "frontend": "FBCA04",
        "infra": "006B75",
        "blocked": "B60205",
        "in-progress": "FEF2C0",
        "ready-for-review": "0E8A16",
    }
    for name, color in labels.items():
        subprocess.run(
            ["gh", "label", "create", name, "--color", color, "--force", "--repo", REPO],
            capture_output=True,
        )


def detect_labels(text: str) -> list[str]:
    """Auto-detect labels from task content."""
    labels = []
    lower = text.lower()
    if any(
        w in lower
        for w in [
            "api",
            "model",
            "schema",
            "migration",
            "route",
            "service",
            "backend",
            "python",
            "fastapi",
        ]
    ):
        labels.append("backend")
    if any(w in lower for w in ["component", "page", "ui", "frontend", "react", "tsx", "css"]):
        labels.append("frontend")
    if any(w in lower for w in ["docker", "nginx", "deploy", "ci", "infra", "config"]):
        labels.append("infra")
    return labels


def parse_blueprint(path: Path) -> dict:
    """Parse blueprint markdown into structured data."""
    content = path.read_text()

    # Extract title (first # heading)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else path.stem

    # Extract goal/summary (text between first heading and first ## heading)
    goal_match = re.search(r"^#\s+.+?\n(.*?)(?=^##\s)", content, re.MULTILINE | re.DOTALL)
    goal = goal_match.group(1).strip() if goal_match else ""

    # Extract phases (## Phase or ## Step or ## numbered sections)
    phases = []
    phase_pattern = re.compile(
        r"^##\s+(?:Phase\s+\d+[:.]\s*|Step\s+\d+[:.]\s*|\d+\.\s*)?(.+)$", re.MULTILINE
    )
    phase_matches = list(phase_pattern.finditer(content))

    for i, match in enumerate(phase_matches):
        start = match.end()
        end = phase_matches[i + 1].start() if i + 1 < len(phase_matches) else len(content)
        phase_body = content[start:end].strip()

        # Extract tasks within phase (### headings)
        tasks = []
        task_pattern = re.compile(r"^###\s+(?:Task\s+[\d.]+[:.]\s*)?(.+)$", re.MULTILINE)
        task_matches = list(task_pattern.finditer(phase_body))

        if task_matches:
            for j, tmatch in enumerate(task_matches):
                tstart = tmatch.end()
                tend = task_matches[j + 1].start() if j + 1 < len(task_matches) else len(phase_body)
                task_body = phase_body[tstart:tend].strip()
                tasks.append({"title": tmatch.group(1).strip(), "body": task_body})
        else:
            # No sub-tasks, the phase itself is the task
            tasks.append({"title": match.group(1).strip(), "body": phase_body})

        phases.append(
            {
                "title": match.group(1).strip(),
                "tasks": tasks,
            }
        )

    return {"title": title, "goal": goal, "phases": phases}


def create_issues(blueprint: dict, dry_run: bool = False) -> list[dict]:
    """Create GitHub Issues from parsed blueprint."""
    created = []

    # Create epic issue
    epic_body = f"## Goal\n{blueprint['goal']}\n\n## Phases\n"
    for i, phase in enumerate(blueprint["phases"], 1):
        epic_body += f"- [ ] Phase {i}: {phase['title']}\n"

    if dry_run:
        print(f"[DRY RUN] Epic: {blueprint['title']}")
        epic_number = 0
    else:
        result = run_gh(
            [
                "issue",
                "create",
                "--title",
                f"[Epic] {blueprint['title']}",
                "--body",
                epic_body,
                "--label",
                "epic",
            ]
        )
        epic_number = int(re.search(r"/(\d+)$", result).group(1)) if result else 0
        created.append(
            {"number": epic_number, "title": f"[Epic] {blueprint['title']}", "type": "epic"}
        )
        print(f"Created epic #{epic_number}: {blueprint['title']}")

    # Create task issues per phase
    prev_task_numbers = []
    for i, phase in enumerate(blueprint["phases"], 1):
        current_phase_numbers = []
        for j, task in enumerate(phase["tasks"]):
            task_title = f"[P{i}] {task['title']}"
            task_body = f"Part of #{epic_number}\n\n"
            if prev_task_numbers:
                task_body += f"Depends on: {', '.join(f'#{n}' for n in prev_task_numbers)}\n\n"
            task_body += f"## Details\n{task['body']}\n"

            labels = ["feature"] + detect_labels(task["body"])
            label_arg = ",".join(labels)

            if dry_run:
                print(f"[DRY RUN] Task: {task_title} (labels: {label_arg})")
                current_phase_numbers.append(0)
            else:
                result = run_gh(
                    [
                        "issue",
                        "create",
                        "--title",
                        task_title,
                        "--body",
                        task_body,
                        "--label",
                        label_arg,
                    ]
                )
                num = int(re.search(r"/(\d+)$", result).group(1)) if result else 0
                current_phase_numbers.append(num)
                created.append({"number": num, "title": task_title, "type": "task", "phase": i})
                print(f"Created task #{num}: {task_title}")

        prev_task_numbers = current_phase_numbers

    return created


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 blueprint-to-issues.py <blueprint-path> [--dry-run]")
        sys.exit(1)

    path = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv

    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    print("Ensuring standard labels exist...")
    if not dry_run:
        ensure_labels()

    print(f"Parsing blueprint: {path}")
    blueprint = parse_blueprint(path)

    print(f"\nTitle: {blueprint['title']}")
    print(f"Phases: {len(blueprint['phases'])}")
    for i, p in enumerate(blueprint["phases"], 1):
        print(f"  Phase {i}: {p['title']} ({len(p['tasks'])} tasks)")

    print("\nCreating issues...")
    created = create_issues(blueprint, dry_run)

    print(f"\n{'=' * 60}")
    print(f"Summary: Created {len(created)} issues")
    print(f"{'=' * 60}")
    for item in created:
        prefix = "+" if item["type"] == "epic" else "  -"
        print(f"{prefix} #{item['number']} {item['title']}")


if __name__ == "__main__":
    main()
