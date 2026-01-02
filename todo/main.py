"""Typer CLI entry points for Todo app."""

import typer
from rich.console import Console
from rich.table import Table

from . import storage
from .app import run_app

app = typer.Typer(
    name="todo",
    help="A terminal-based todo list with vim-style navigation.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def view() -> None:
    """Launch the interactive todo list viewer."""
    run_app()


@app.command()
def create(title: str = typer.Argument(..., help="The task title")) -> None:
    """Create a new task."""
    task = storage.add_task(title)
    console.print(f"[green]✓[/green] Created task #{task.id}: {task.title}")


@app.command()
def clear() -> None:
    """Remove all completed tasks."""
    count = storage.clear_completed()
    if count > 0:
        console.print(f"[green]✓[/green] Cleared {count} completed task(s)")
    else:
        console.print("[yellow]No completed tasks to clear[/yellow]")


@app.command()
def list() -> None:
    """List all tasks (non-interactive)."""
    tasks = storage.load_tasks()
    
    if not tasks:
        console.print("[dim]No tasks yet. Use 'todo create' or 'todo view' to add tasks.[/dim]")
        return
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("✓", width=3)
    table.add_column("ID", width=4)
    table.add_column("Title", min_width=30)
    table.add_column("Status", width=10)
    table.add_column("Created", width=8)
    
    for task in tasks:
        checkbox = "[green][x][/green]" if task.is_completed() else "[ ]"
        status_style = "green" if task.is_completed() else "yellow"
        title_style = "dim strike" if task.is_completed() else ""
        
        table.add_row(
            checkbox,
            str(task.id),
            f"[{title_style}]{task.title}[/{title_style}]" if title_style else task.title,
            f"[{status_style}]{task.status.capitalize()}[/{status_style}]",
            task.relative_time(),
        )
    
    console.print(table)


if __name__ == "__main__":
    app()

