---
name: github-pm
description: >-
  GitHub Project Management utilities for issue tracking and workflow automation.
version: 0.1.0
tools: Bash
---

# GitHub PM

## FSM — GitHub PM State Machine

```
┌──────────┐  /pm:create  ┌──────────────┐  /pm:start  ┌──────────────┐
│  BACKLOG │────────────►│   OPEN       │───────────►│  IN PROGRESS │
└──────────┘              └──────────────┘             └──────┬───────┘
                                                              │ /pm:sync
                                                              ▼
                                                       ┌──────────────┐
                                                       │  REVIEWED    │
                                                       └──────┬───────┘
                                                              │ /pm:close
                                                              ▼
                                                       ┌──────────────┐
                                                       │    CLOSED    │
                                                       └──────────────┘
```

Project management system using GitHub Issues as source of truth.
Integrates with blueprint, forge, executor, and git-worktrees skills.

## Commands

| Command | Purpose |
|---------|---------|
| `/pm:create` | Create issues from blueprint or description |
| `/pm:list` | List open issues (grouped by status) |
| `/pm:next` | Suggest next priority task |
| `/pm:start` | Begin work on issue (worktree + label) |
| `/pm:sync` | Push progress update to issue |
| `/pm:close` | Close issue with summary |
| `/pm:status` | Project dashboard |

## Automation

- **Blueprint -> Issues**: `scripts/blueprint-to-issues.py` parses blueprint and creates linked issues
- **Commit -> Issue sync**: Hook auto-detects `#N` refs and comments on issues
- **Session startup**: Load open issues into context for continuity

## Integration Points

- **blueprint** skill -> `/pm:create <blueprint-path>` auto-creates issues
- **forge** skill -> Each forge stage maps to issue lifecycle
- **git-worktrees** -> Branch naming: `feature/<slug>-#<number>`
- **executor** -> Progress sync on each phase completion

## Repo

GitHub: `JonesHong/workshop` (private)
