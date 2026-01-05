"""Custom Textual widgets for the Todo app."""

from textual.widgets import Static, DataTable
from rich.text import Text

from .models import Task, Workspace


class TaskTable(DataTable):
    """Custom DataTable for displaying tasks with styling."""
    
    DEFAULT_CSS = """
    TaskTable {
        height: 1fr;
        margin: 1 2;
    }
    
    TaskTable > .datatable--cursor {
        background: #3b4261;
    }
    
    TaskTable > .datatable--header {
        background: #1a1b26;
        color: #a9b1d6;
        text-style: bold;
    }
    """
    
    def __init__(self, classes: str = "") -> None:
        super().__init__(cursor_type="row", classes=classes)
        self.show_header = True
        self.zebra_stripes = True
    
    def on_mount(self) -> None:
        """Set up columns when widget is mounted."""
        self.add_column("✓", width=5, key="check")
        self.add_column("Title", width=50, key="title")
        self.add_column("Priority", width=10, key="priority")
        self.add_column("Status", width=12, key="status")
        self.add_column("Created", width=10, key="created")
    
    def populate(self, tasks: list[Task]) -> None:
        """Fill the table with tasks."""
        self.clear()
        
        for task in tasks:
            checkbox = self._format_checkbox(task)
            title = self._format_title(task)
            priority = self._format_priority(task)
            status = self._format_status(task)
            created = self._format_created(task)
            
            self.add_row(checkbox, title, priority, status, created, key=str(task.id))
    
    def _format_checkbox(self, task: Task) -> Text:
        """Format the checkbox column."""
        if task.is_completed():
            return Text("[x]", style="bold green")
        return Text("[ ]", style="dim")
    
    def _format_title(self, task: Task) -> Text:
        """Format the title column."""
        if task.is_completed():
            return Text(task.title, style="dim strike")
        return Text(task.title)
    
    def _format_priority(self, task: Task) -> Text:
        """Format the priority column with colors."""
        if task.priority == "high":
            return Text("High", style="bold red")
        elif task.priority == "medium":
            return Text("Medium", style="bold yellow")
        elif task.priority == "low":
            return Text("Low", style="dim")
        return Text("-", style="dim")
    
    def _format_status(self, task: Task) -> Text:
        """Format the status column with colors."""
        if task.is_completed():
            return Text("Completed", style="bold green")
        return Text("Pending", style="bold yellow")
    
    def _format_created(self, task: Task) -> Text:
        """Format the created timestamp as date."""
        return Text(task.formatted_date(), style="dim")
    
    def get_selected_task_id(self) -> int | None:
        """Get the ID of the currently selected task."""
        if self.row_count == 0:
            return None
        
        row_key = self.coordinate_to_cell_key(self.cursor_coordinate).row_key
        if row_key:
            return int(row_key.value)
        return None


class WorkspaceTable(DataTable):
    """Custom DataTable for displaying workspaces."""
    
    DEFAULT_CSS = """
    WorkspaceTable {
        height: 1fr;
        margin: 1 2;
    }
    
    WorkspaceTable > .datatable--cursor {
        background: #3b4261;
    }
    
    WorkspaceTable > .datatable--header {
        background: #1a1b26;
        color: #a9b1d6;
        text-style: bold;
    }
    """
    
    # Special ID for "All Tasks" option
    ALL_TASKS_ID = -1
    
    def __init__(self) -> None:
        super().__init__(cursor_type="row")
        self.show_header = True
        self.zebra_stripes = True
    
    def on_mount(self) -> None:
        """Set up columns when widget is mounted."""
        self.add_column("", width=4, key="icon")
        self.add_column("Workspace", width=40, key="name")
        self.add_column("Tasks", width=10, key="tasks")
    
    def populate(self, workspaces: list[Workspace], task_counts: dict[int, int], total_tasks: int) -> None:
        """Fill the table with workspaces."""
        self.clear()
        
        # Add "All Tasks" option first
        self.add_row(
            Text("📋", style="bold"),
            Text("All Tasks", style="bold #7aa2f7"),
            Text(str(total_tasks), style="dim"),
            key=str(self.ALL_TASKS_ID)
        )
        
        # Add each workspace
        for ws in workspaces:
            count = task_counts.get(ws.id, 0)
            self.add_row(
                Text("📁", style="bold #f7768e"),
                Text(ws.name),
                Text(str(count), style="dim"),
                key=str(ws.id)
            )
    
    def get_selected_workspace_id(self) -> int | None:
        """Get the ID of the currently selected workspace. Returns ALL_TASKS_ID for global view."""
        if self.row_count == 0:
            return None
        
        row_key = self.coordinate_to_cell_key(self.cursor_coordinate).row_key
        if row_key:
            return int(row_key.value)
        return None


class HelpBar(Static):
    """Bottom help bar showing available commands."""
    
    DEFAULT_CSS = """
    HelpBar {
        height: 1;
        dock: bottom;
        background: #1a1b26;
        color: #565f89;
        padding: 0 1;
    }
    """
    
    def __init__(self, mode: str = "workspaces") -> None:
        super().__init__()
        self.mode = mode  # "workspaces" or "tasks"
    
    def set_mode(self, mode: str) -> None:
        """Set the current mode and refresh."""
        self.mode = mode
        self.refresh()
    
    def render(self) -> Text:
        """Render the help bar based on current mode."""
        help_text = Text()
        
        if self.mode == "workspaces":
            commands = [
                ("j/k", "navigate"),
                ("Enter", "open"),
                ("a", "add"),
                ("e", "edit"),
                ("dd", "delete"),
                ("q", "quit"),
            ]
        else:  # tasks mode
            commands = [
                ("j/k", "navigate"),
                ("J/K", "move"),
                ("x", "toggle"),
                ("p", "priority"),
                ("a", "add"),
                ("e", "edit"),
                ("dd", "delete"),
                ("Bksp", "back"),
                ("q", "quit"),
            ]
        
        for key, action in commands:
            help_text.append(f" {key}", style="bold #7aa2f7")
            help_text.append(f":{action} ", style="#565f89")
        
        return help_text


class ViewHeader(Static):
    """Header showing current view name (workspace or All Tasks)."""
    
    DEFAULT_CSS = """
    ViewHeader {
        height: 3;
        padding: 1 2;
        background: #1a1b26;
        color: #7aa2f7;
        text-align: center;
        text-style: bold;
    }
    """
    
    def __init__(self, title: str = "Workspaces") -> None:
        super().__init__()
        self.title = title
    
    def set_title(self, title: str) -> None:
        """Update the title."""
        self.title = title
        self.refresh()
    
    def render(self) -> Text:
        """Render the header."""
        return Text(f"─── {self.title} ───", style="bold #7aa2f7")


class InputBar(Static):
    """Input bar for adding/editing tasks."""
    
    DEFAULT_CSS = """
    InputBar {
        height: 3;
        dock: bottom;
        background: #1a1b26;
        border-top: solid #3b4261;
        padding: 0 1;
    }
    """
    
    def __init__(self, prompt: str = "New task: ") -> None:
        super().__init__()
        self.prompt = prompt
    
    def set_prompt(self, prompt: str) -> None:
        """Update the prompt text."""
        self.prompt = prompt
        self.refresh()
    
    def render(self) -> Text:
        """Render the input prompt."""
        return Text(self.prompt, style="bold #7aa2f7")

