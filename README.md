# Todo CLI

A terminal-based todo list application with vim-style keyboard navigation.

## Installation

```bash
pip install -e .
```

## Usage

### Launch Interactive View

```bash
todo view
```

### Quick Commands

```bash
todo create "Buy groceries"    # Add a new task
todo clear                     # Remove completed tasks
```

## Keyboard Shortcuts (in interactive mode)

| Key | Action |
|-----|--------|
| `j` / `↓` | Move selection down |
| `k` / `↑` | Move selection up |
| `x` / `Space` | Toggle task complete/pending |
| `dd` | Delete selected task |
| `a` | Add new task |
| `e` | Edit selected task |
| `q` / `Esc` | Quit |

## Data Storage

Tasks are stored in `~/.todo/tasks.json`.

