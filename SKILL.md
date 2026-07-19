---
name: github-pm
description: "pm, github, create, project, issue, manage, tasks, 建 issue, 開 GitHub issue, 查看 backlog"
version: 0.1.0
tools: Bash
disable-model-invocation: true
---

# GitHub PM

## FSM — GitHub PM State Machine

```
┌──────────┐    create    ┌──────────────┐    start    ┌──────────────┐
│  BACKLOG │────────────►│   OPEN       │───────────►│  IN PROGRESS │
└──────────┘              └──────────────┘             └──────┬───────┘
                                                              │ sync
                                                              ▼
                                                       ┌──────────────┐
                                                       │  REVIEWED    │
                                                       └──────┬───────┘
                                                              │ close
                                                              ▼
                                                       ┌──────────────┐
                                                       │    CLOSED    │
                                                       └──────────────┘
```

Project management system using GitHub Issues as source of truth.
Integrates with blueprint, forge, executor, and git-worktrees skills.

> **Invocation:** triggered by natural language (e.g. "建 issue", "查看 backlog",
> "close issue #42"), not slash commands. The actions below are capabilities the
> skill runs via the `gh` CLI — describe the intent and the matching action fires.

## Actions

| Action | Trigger phrase (example) | Purpose |
|--------|--------------------------|---------|
| create | "建 issue from this description" | Create issues from blueprint or description |
| list   | "list open issues" / "查看 backlog" | List open issues (grouped by status) |
| next   | "what's the next task?" | Suggest next priority task |
| start  | "start work on #42" | Begin work on issue (worktree + label) |
| sync   | "sync progress to #42" | Push progress update to issue |
| close  | "close #42 with summary" | Close issue with summary |
| status | "show project dashboard" | Project dashboard |

## Automation

- **Blueprint -> Issues**: `scripts/blueprint-to-issues.py` parses blueprint and creates linked issues
- **Commit -> Issue sync**: Hook auto-detects `#N` refs and comments on issues
- **Session startup**: Load open issues into context for continuity

## Integration Points

- **blueprint** skill -> hand it a blueprint path to auto-create linked issues
- **forge** skill -> Each forge stage maps to issue lifecycle
- **git-worktrees** -> Branch naming: `feature/<slug>-#<number>`
- **executor** -> Progress sync on each phase completion

## Repo

GitHub: `JonesHong/workshop` (private)
