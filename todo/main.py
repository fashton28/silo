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
def o() -> None:
    """Launch the interactive todo list viewer."""
    run_app()

@app.command()
def clear() -> None:
    """Remove all completed tasks and archive them to history."""
    count = storage.clear_completed()
    if count > 0:
        console.print(f"[green]✓[/green] Archived {count} completed task(s) to history")
    else:
        console.print("[yellow]No completed tasks to clear[/yellow]")


@app.command()
def history(
    clear_all: bool = typer.Option(False, "--clear", "-c", help="Clear all history")
) -> None:
    """View or clear completed task history."""
    if clear_all:
        count = storage.clear_history()
        if count > 0:
            console.print(f"[green]✓[/green] Cleared {count} task(s) from history")
        else:
            console.print("[yellow]History is already empty[/yellow]")
        return
    
    tasks = storage.load_history()
    
    if not tasks:
        console.print("[dim]No history yet. Completed tasks appear here after running 'todo clear'.[/dim]")
        return
    
    table = Table(show_header=True, header_style="bold", title="[bold]Completed Task History[/bold]")
    table.add_column("ID", width=4)
    table.add_column("Title", min_width=40)
    table.add_column("Created", width=10)
    table.add_column("Completed", width=10)
    
    for task in reversed(tasks):  # Show most recent first
        table.add_row(
            str(task.id),
            task.title,
            task.formatted_date(),
            _format_date_from_iso(task.completed_at) if task.completed_at else "-",
        )
    
    console.print(table)
    console.print(f"\n[dim]{len(tasks)} completed task(s) in history. Use 'todo history --clear' to delete.[/dim]")


def _format_date_from_iso(iso_time: str) -> str:
    """Convert ISO timestamp to date string."""
    from datetime import datetime
    
    try:
        dt = datetime.fromisoformat(iso_time)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "-"


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
    table.add_column("Created", width=12)
    
    for task in tasks:
        checkbox = "[green][x][/green]" if task.is_completed() else "[ ]"
        status_style = "green" if task.is_completed() else "yellow"
        title_style = "dim strike" if task.is_completed() else ""
        
        table.add_row(
            checkbox,
            str(task.id),
            f"[{title_style}]{task.title}[/{title_style}]" if title_style else task.title,
            f"[{status_style}]{task.status.capitalize()}[/{status_style}]",
            task.formatted_date(),
        )
    
    console.print(table)


if __name__ == "__main__":
    app()

