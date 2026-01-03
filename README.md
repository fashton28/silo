```
 ███████╗██╗██╗      ██████╗ 
 ██╔════╝██║██║     ██╔═══██╗
 ███████╗██║██║     ██║   ██║
 ╚════██║██║██║     ██║   ██║
 ███████║██║███████╗╚██████╔╝
 ╚══════╝╚═╝╚══════╝ ╚═════╝ 
```

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
todo clear                     # Archive completed tasks to history
todo history                   # View completed task history
todo history --clear           # Delete all history
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

- Active tasks: `~/.todo/tasks.json`
- Completed history: `~/.todo/history.json`

