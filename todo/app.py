"""Textual TUI application for Todo CLI."""

from textual.app import App, ComposeResult
from textual.widgets import Input, Footer
from textual.containers import Container, Vertical
from textual.binding import Binding
from textual import events

from .widgets import TaskTable, WorkspaceTable, HelpBar, ViewHeader
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
        self.editing_id: int | None = None  # Track item being edited
        self.input_mode: str | None = None  # "add_task", "edit_task", "add_workspace", "edit_workspace"
        self.view_mode: str = "workspaces"  # "workspaces" or "tasks"
        self.current_workspace_id: int | None = None  # None means "All Tasks" view
        self.current_workspace_name: str = "All Tasks"
    
    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        with Vertical(id="main-container"):
            yield ViewHeader("Workspaces")
            yield WorkspaceTable()
            yield TaskTable(classes="hidden")
            yield Input(placeholder="Enter title...", id="task-input", classes="hidden")
            yield HelpBar(mode="workspaces")
    
    def on_mount(self) -> None:
        """Initialize the app when mounted."""
        self.refresh_workspaces()
        self.query_one(WorkspaceTable).focus()
    
    # ─── Refresh Methods ───────────────────────────────────────────────────────
    
    def refresh_workspaces(self, row_offset: int = 0) -> None:
        """Reload and display workspaces."""
        table = self.query_one(WorkspaceTable)
        
        current_row = table.cursor_row if table.row_count > 0 else 0
        target_row = current_row + row_offset
        
        workspaces = storage.load_workspaces()
        all_tasks = storage.load_tasks()
        
        # Calculate task counts per workspace
        task_counts = {}
        for ws in workspaces:
            task_counts[ws.id] = storage.get_workspace_task_count(ws.id)
        
        table.populate(workspaces, task_counts, len(all_tasks))
        
        if table.row_count > 0:
            target_row = max(0, min(target_row, table.row_count - 1))
            table.move_cursor(row=target_row)
    
    def refresh_tasks(self, row_offset: int = 0) -> None:
        """Reload and display tasks for current workspace."""
        table = self.query_one(TaskTable)
        
        current_row = table.cursor_row if table.row_count > 0 else 0
        target_row = current_row + row_offset
        
        # Load tasks filtered by workspace (None = all tasks)
        tasks = storage.load_tasks_by_workspace(self.current_workspace_id)
        table.populate(tasks)
        
        if table.row_count > 0:
            target_row = max(0, min(target_row, table.row_count - 1))
            table.move_cursor(row=target_row)
    
    # ─── View Switching ────────────────────────────────────────────────────────
    
    def enter_workspace(self, workspace_id: int | None, workspace_name: str) -> None:
        """Enter a workspace to view its tasks."""
        self.current_workspace_id = workspace_id
        self.current_workspace_name = workspace_name
        self.view_mode = "tasks"
        
        # Update UI
        self.query_one(ViewHeader).set_title(workspace_name)
        self.query_one(WorkspaceTable).add_class("hidden")
        self.query_one(TaskTable).remove_class("hidden")
        self.query_one(HelpBar).set_mode("tasks")
        
        self.refresh_tasks()
        self.query_one(TaskTable).focus()
    
    def exit_to_workspaces(self) -> None:
        """Go back to workspace list."""
        self.view_mode = "workspaces"
        self.current_workspace_id = None
        self.current_workspace_name = "All Tasks"
        
        # Update UI
        self.query_one(ViewHeader).set_title("Workspaces")
        self.query_one(TaskTable).add_class("hidden")
        self.query_one(WorkspaceTable).remove_class("hidden")
        self.query_one(HelpBar).set_mode("workspaces")
        
        self.refresh_workspaces()
        self.query_one(WorkspaceTable).focus()
    
    # ─── Key Handling ──────────────────────────────────────────────────────────
    
    def on_key(self, event: events.Key) -> None:
        """Handle keyboard input."""
        key = event.key
        task_input = self.query_one("#task-input", Input)
        
        # If input is visible and focused, let it handle input
        if not task_input.has_class("hidden") and task_input.has_focus:
            return
        
        if self.view_mode == "workspaces":
            self._handle_workspace_key(key)
        else:
            self._handle_task_key(key)
    
    def _handle_workspace_key(self, key: str) -> None:
        """Handle keys in workspace view."""
        table = self.query_one(WorkspaceTable)
        
        # Navigation
        if key == "j" or key == "down":
            table.action_cursor_down()
            self.last_key = None
        
        elif key == "k" or key == "up":
            table.action_cursor_up()
            self.last_key = None
        
        # Enter workspace
        elif key == "enter":
            ws_id = table.get_selected_workspace_id()
            if ws_id is not None:
                if ws_id == WorkspaceTable.ALL_TASKS_ID:
                    self.enter_workspace(None, "All Tasks")
                else:
                    workspaces = storage.load_workspaces()
                    ws = next((w for w in workspaces if w.id == ws_id), None)
                    if ws:
                        self.enter_workspace(ws.id, ws.name)
            self.last_key = None
        
        # Add workspace
        elif key == "a":
            self.show_input("add_workspace")
            self.last_key = None
        
        # Edit workspace
        elif key == "e":
            ws_id = table.get_selected_workspace_id()
            if ws_id is not None and ws_id != WorkspaceTable.ALL_TASKS_ID:
                self.editing_id = ws_id
                workspaces = storage.load_workspaces()
                current_name = next((w.name for w in workspaces if w.id == ws_id), "")
                self.show_input("edit_workspace", current_name)
            self.last_key = None
        
        # Delete workspace with dd
        elif key == "d":
            if self.last_key == "d":
                ws_id = table.get_selected_workspace_id()
                if ws_id is not None and ws_id != WorkspaceTable.ALL_TASKS_ID:
                    storage.delete_workspace(ws_id)
                    self.refresh_workspaces()
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
    
    def _handle_task_key(self, key: str) -> None:
        """Handle keys in task view."""
        table = self.query_one(TaskTable)
        
        # Navigation
        if key == "j" or key == "down":
            table.action_cursor_down()
            self.last_key = None
        
        elif key == "k" or key == "up":
            table.action_cursor_up()
            self.last_key = None
        
        # Move task down (Shift+J)
        elif key == "J":
            task_id = table.get_selected_task_id()
            if task_id is not None:
                if storage.move_task_down(task_id):
                    self.refresh_tasks(row_offset=1)
            self.last_key = None
        
        # Move task up (Shift+K)
        elif key == "K":
            task_id = table.get_selected_task_id()
            if task_id is not None:
                if storage.move_task_up(task_id):
                    self.refresh_tasks(row_offset=-1)
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
            self.show_input("add_task")
            self.last_key = None
        
        # Edit task
        elif key == "e":
            task_id = table.get_selected_task_id()
            if task_id is not None:
                self.editing_id = task_id
                tasks = storage.load_tasks()
                current_title = next((t.title for t in tasks if t.id == task_id), "")
                self.show_input("edit_task", current_title)
            self.last_key = None
        
        # Delete task with dd
        elif key == "d":
            if self.last_key == "d":
                task_id = table.get_selected_task_id()
                if task_id is not None:
                    storage.delete_task(task_id)
                    self.refresh_tasks()
                self.last_key = None
            else:
                self.last_key = "d"
        
        # Go back to workspaces
        elif key == "backspace":
            self.exit_to_workspaces()
            self.last_key = None
        
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
    
    # ─── Input Handling ────────────────────────────────────────────────────────
    
    def show_input(self, mode: str, initial_value: str = "") -> None:
        """Show the input field."""
        self.input_mode = mode
        task_input = self.query_one("#task-input", Input)
        task_input.remove_class("hidden")
        task_input.value = initial_value
        
        placeholders = {
            "add_task": "Enter new task title...",
            "edit_task": "Edit task title...",
            "add_workspace": "Enter new workspace name...",
            "edit_workspace": "Edit workspace name...",
        }
        task_input.placeholder = placeholders.get(mode, "Enter text...")
        task_input.focus()
    
    def hide_input(self) -> None:
        """Hide the input field and reset state."""
        task_input = self.query_one("#task-input", Input)
        task_input.add_class("hidden")
        task_input.value = ""
        self.input_mode = None
        self.editing_id = None
        
        # Refocus the appropriate table
        if self.view_mode == "workspaces":
            self.query_one(WorkspaceTable).focus()
        else:
            self.query_one(TaskTable).focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        value = event.value.strip()
        
        if value:
            if self.input_mode == "add_task":
                storage.add_task(value, self.current_workspace_id)
                self.refresh_tasks()
            elif self.input_mode == "edit_task" and self.editing_id is not None:
                storage.update_task_title(self.editing_id, value)
                self.refresh_tasks()
            elif self.input_mode == "add_workspace":
                storage.add_workspace(value)
                self.refresh_workspaces()
            elif self.input_mode == "edit_workspace" and self.editing_id is not None:
                storage.update_workspace_name(self.editing_id, value)
                self.refresh_workspaces()
        
        self.hide_input()
    
    def action_cancel_or_quit(self) -> None:
        """Cancel input, go back, or quit the app."""
        task_input = self.query_one("#task-input", Input)
        
        if not task_input.has_class("hidden"):
            self.hide_input()
        elif self.view_mode == "tasks":
            self.exit_to_workspaces()
        else:
            self.exit()


def run_app() -> None:
    """Run the Todo TUI application."""
    app = TodoApp()
    app.run()
