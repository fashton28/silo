"""Textual TUI application for Todo CLI."""

from textual.app import App, ComposeResult
from textual.widgets import Input, Footer
from textual.containers import Container, Vertical
from textual.binding import Binding
from textual import events

from .widgets import Header, TaskTable, HelpBar
from . import storage


class TodoApp(App):
    """Interactive todo list TUI application."""
    
    CSS = """
    Screen {
        background: #1a1b26;
    }
    
    #main-container {
        height: 100%;
        padding: 0;
    }
    
    #task-input {
        dock: bottom;
        height: 3;
        margin: 0 2;
        background: #24283b;
        border: solid #3b4261;
        padding: 0 1;
    }
    
    #task-input:focus {
        border: solid #7aa2f7;
    }
    
    .hidden {
        display: none;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
        Binding("escape", "cancel_or_quit", "Cancel/Quit", show=False),
    ]
    
    def __init__(self) -> None:
        super().__init__()
        self.last_key: str | None = None  # Track last key for dd sequence
        self.editing_task_id: int | None = None  # Track task being edited
        self.input_mode: str | None = None  # "add" or "edit"
    
    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        with Vertical(id="main-container"):
            yield Header()
            yield TaskTable()
            yield Input(placeholder="Enter task title...", id="task-input", classes="hidden")
            yield HelpBar()
    
    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        self.refresh_tasks()
        # Focus the table
        self.query_one(TaskTable).focus()
    
    def refresh_tasks(self) -> None:
        """Reload and display tasks from storage."""
        tasks = storage.load_tasks()
        table = self.query_one(TaskTable)
        table.populate(tasks)
    
    def on_key(self, event: events.Key) -> None:
        """Handle keyboard input for vim-style navigation."""
        key = event.key
        table = self.query_one(TaskTable)
        task_input = self.query_one("#task-input", Input)
        
        # If input is visible and focused, let it handle input
        if not task_input.has_class("hidden") and task_input.has_focus:
            return
        
        # Vim navigation
        if key == "j" or key == "down":
            table.action_cursor_down()
            self.last_key = None
        
        elif key == "k" or key == "up":
            table.action_cursor_up()
            self.last_key = None
        
        # Toggle completion
        elif key == "x" or key == "space":
            task_id = table.get_selected_task_id()
            if task_id is not None:
                storage.toggle_task(task_id)
                self.refresh_tasks()
            self.last_key = None
        
        # Cycle priority
        elif key == "p":
            task_id = table.get_selected_task_id()
            if task_id is not None:
                storage.cycle_task_priority(task_id)
                self.refresh_tasks()
            self.last_key = None
        
        # Add new task
        elif key == "a":
            self.show_input("add")
            self.last_key = None
        
        # Edit task
        elif key == "e":
            task_id = table.get_selected_task_id()
            if task_id is not None:
                self.editing_task_id = task_id
                tasks = storage.load_tasks()
                current_title = next((t.title for t in tasks if t.id == task_id), "")
                self.show_input("edit", current_title)
            self.last_key = None
        
        # Delete with dd
        elif key == "d":
            if self.last_key == "d":
                task_id = table.get_selected_task_id()
                if task_id is not None:
                    storage.delete_task(task_id)
                    self.refresh_tasks()
                self.last_key = None
            else:
                self.last_key = "d"
        
        # G to go to bottom
        elif key == "G":
            if table.row_count > 0:
                table.move_cursor(row=table.row_count - 1)
            self.last_key = None
        
        # gg to go to top
        elif key == "g":
            if self.last_key == "g":
                table.move_cursor(row=0)
                self.last_key = None
            else:
                self.last_key = "g"
        
        else:
            self.last_key = None
    
    def show_input(self, mode: str, initial_value: str = "") -> None:
        """Show the input field for adding/editing tasks."""
        self.input_mode = mode
        task_input = self.query_one("#task-input", Input)
        task_input.remove_class("hidden")
        task_input.value = initial_value
        
        if mode == "add":
            task_input.placeholder = "Enter new task title..."
        else:
            task_input.placeholder = "Edit task title..."
        
        task_input.focus()
    
    def hide_input(self) -> None:
        """Hide the input field and reset state."""
        task_input = self.query_one("#task-input", Input)
        task_input.add_class("hidden")
        task_input.value = ""
        self.input_mode = None
        self.editing_task_id = None
        self.query_one(TaskTable).focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        value = event.value.strip()
        
        if value:
            if self.input_mode == "add":
                storage.add_task(value)
            elif self.input_mode == "edit" and self.editing_task_id is not None:
                storage.update_task_title(self.editing_task_id, value)
            
            self.refresh_tasks()
        
        self.hide_input()
    
    def action_cancel_or_quit(self) -> None:
        """Cancel input or quit the app."""
        task_input = self.query_one("#task-input", Input)
        
        if not task_input.has_class("hidden"):
            self.hide_input()
        else:
            self.exit()


def run_app() -> None:
    """Run the Todo TUI application."""
    app = TodoApp()
    app.run()

