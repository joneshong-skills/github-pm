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

- **Issue Lifecycle Management** -- Create, start, sync, and close issues through slash commands
- **Blueprint-to-Issues Pipeline** -- Automatically generate linked issues from blueprint documents
- **Worktree Integration** -- Start work on an issue with automatic branch and worktree creation
- **Progress Sync** -- Push progress updates to issues via commit references and comments
- **Priority Suggestions** -- Get next-task recommendations based on project state
- **Project Dashboard** -- View project status grouped by issue lifecycle stage

## Usage

### Commands

| Command | Purpose |
|---------|---------|
| `/pm:create` | Create issues from blueprint or description |
| `/pm:list` | List open issues grouped by status |
| `/pm:next` | Suggest next priority task |
| `/pm:start` | Begin work on issue (worktree + label) |
| `/pm:sync` | Push progress update to issue |
| `/pm:close` | Close issue with summary |
| `/pm:status` | Project dashboard |

### Examples

```
/pm:create docs/plans/feature-x-blueprint.md

/pm:start #42

/pm:sync #42

/pm:status
```

## Workflow

```
Backlog --> Open --> In Progress --> Reviewed --> Closed
```

1. **Create** -- Generate issues from blueprints or descriptions (`/pm:create`)
2. **Start** -- Pick up an issue, create worktree and branch (`/pm:start`)
3. **Sync** -- Push progress updates during development (`/pm:sync`)
4. **Close** -- Complete issue with summary (`/pm:close`)

## Integration

| Skill | Relationship |
|-------|-------------|
| `blueprint` | `/pm:create <blueprint>` auto-creates linked issues |
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
