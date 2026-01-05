# Silo Todo

A beautiful terminal-based todo list application with vim-style keyboard navigation, workspaces, and priorities.

## Features

- **Workspaces** - Organize tasks into separate workspaces (School, Work, Personal, etc.)
- **Priorities** - Set High/Medium/Low priority on tasks
- **Vim-style Navigation** - Navigate with `j`/`k`, delete with `dd`
- **Task Reordering** - Move tasks up/down with `Shift+J`/`Shift+K`
- **Beautiful TUI** - Clean terminal interface built with Textual

## Installation

```bash
pip install silo-todo
```

## Usage

### Launch the App

```bash
silo o
```

This opens the interactive TUI starting with your workspace list.

### CLI Commands

```bash
silo list                      # List all tasks (non-interactive)
silo clear                     # Archive completed tasks to history
silo history                   # View completed task history
silo history --clear           # Delete all history
```

## Keyboard Shortcuts

### Workspace View

| Key | Action |
|-----|--------|
| `j` / `↓` | Move selection down |
| `k` / `↑` | Move selection up |
| `Enter` | Open workspace |
| `a` | Add new workspace |
| `e` | Edit workspace name |
| `dd` | Delete workspace |
| `q` | Quit |

### Task View

| Key | Action |
|-----|--------|
| `j` / `↓` | Move selection down |
| `k` / `↑` | Move selection up |
| `J` (Shift+J) | Move task down |
| `K` (Shift+K) | Move task up |
| `x` / `Space` | Toggle complete/pending |
| `p` | Cycle priority (None → Low → Medium → High) |
| `a` | Add new task |
| `e` | Edit task title |
| `dd` | Delete task |
| `Backspace` | Go back to workspaces |
| `q` / `Esc` | Quit / Go back |

## Data Storage

All data is stored locally in your home directory:

- Workspaces: `~/.todo/workspaces.json`
- Tasks: `~/.todo/tasks.json`
- History: `~/.todo/history.json`

## License

MIT License - see [LICENSE](LICENSE) for details.
