<h1 align="center">GitHub PM</h1>

<p align="center">
  <a href="./README.md"><strong>English</strong></a> | <a href="./README.zh.md">繁體中文</a>
</p>

<p align="center">
  <a href="https://github.com/joneshong-skills/github-pm/stargazers"><img src="https://img.shields.io/github/stars/joneshong-skills/github-pm?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/joneshong-skills/github-pm/blob/main/LICENSE"><img src="https://img.shields.io/github/license/joneshong-skills/github-pm?style=flat-square" alt="License"></a>
</p>

<p align="center">
  GitHub project management utilities -- issue tracking and workflow automation using GitHub Issues as the source of truth.
</p>

---

## Features

- **Issue Lifecycle Management** -- Create, start, sync, and close issues through natural language
- **Blueprint-to-Issues Pipeline** -- Automatically generate linked issues from blueprint documents
- **Worktree Integration** -- Start work on an issue with automatic branch and worktree creation
- **Progress Sync** -- Push progress updates to issues via commit references and comments
- **Priority Suggestions** -- Get next-task recommendations based on project state
- **Project Dashboard** -- View project status grouped by issue lifecycle stage

## Usage

### Actions

Triggered by natural language, not slash commands -- describe the intent and the skill runs the matching action via the `gh` CLI.

| Action | Trigger phrase (example) | Purpose |
|--------|--------------------------|---------|
| create | "create an issue for X" | Create issues from blueprint or description |
| list   | "list open issues" | List open issues grouped by status |
| next   | "what's the next task?" | Suggest next priority task |
| start  | "start work on #42" | Begin work on issue (worktree + label) |
| sync   | "sync progress to #42" | Push progress update to issue |
| close  | "close #42 with a summary" | Close issue with summary |
| status | "show the project dashboard" | Project dashboard |

### Examples

```
"Create issues from docs/plans/feature-x-blueprint.md"

"Start work on issue #42"

"Sync my progress to issue #42"

"Show the project status"
```

## Workflow

```
Backlog --> Open --> In Progress --> Reviewed --> Closed
```

1. **Create** -- Generate issues from blueprints or descriptions
2. **Start** -- Pick up an issue, create worktree and branch
3. **Sync** -- Push progress updates during development
4. **Close** -- Complete issue with summary

## Integration

| Skill | Relationship |
|-------|-------------|
| `blueprint` | hand it a blueprint to auto-create linked issues |
| `forge` | Each forge stage maps to issue lifecycle |
| `git-worktrees` | Branch naming: `feature/<slug>-#<number>` |
| `executor` | Progress sync on each phase completion |

Automation hooks: commit messages with `#N` references auto-comment on issues; session startup loads open issues into context.

## Installation

```bash
# Clone into your Claude skills directory
cp -r github-pm/ ~/.claude/skills/github-pm/
```

**Requirements:** `gh` CLI (authenticated), Claude Code with `Bash` tool.

## License

[MIT](./LICENSE)
