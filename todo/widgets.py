"""Custom Textual widgets for the Todo app."""

from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

from .models import Task


ASCII_HEADER = r"""
 ███████╗██╗██╗      ██████╗ 
 ██╔════╝██║██║     ██╔═══██╗
 ███████╗██║██║     ██║   ██║
 ╚════██║██║██║     ██║   ██║
 ███████║██║███████╗╚██████╔╝
 ╚══════╝╚═╝╚══════╝ ╚═════╝ 
"""


class Header(Static):
    """ASCII art header widget."""
    
    DEFAULT_CSS = """
    Header {
        height: auto;
        padding: 0 1;
        color: #7aa2f7;
        text-align: center;
    }
    """
    
    def render(self) -> Text:
        """Render the ASCII header."""
        text = Text(ASCII_HEADER, style="bold #7aa2f7")
        return text


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
    
    def __init__(self) -> None:
        super().__init__(cursor_type="row")
        self.show_header = True
        self.zebra_stripes = True
    
    def on_mount(self) -> None:
        """Set up columns when widget is mounted."""
        self.add_column("✓", width=5, key="check")
        self.add_column("Title", width=60, key="title")
        self.add_column("Status", width=12, key="status")
        self.add_column("Created", width=10, key="created")
    
    def populate(self, tasks: list[Task]) -> None:
        """Fill the table with tasks."""
        self.clear()
        
        for task in tasks:
            checkbox = self._format_checkbox(task)
            title = self._format_title(task)
            status = self._format_status(task)
            created = self._format_created(task)
            
            self.add_row(checkbox, title, status, created, key=str(task.id))
    
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
    
    def _format_status(self, task: Task) -> Text:
        """Format the status column with colors."""
        if task.is_completed():
            return Text("Completed", style="bold green")
        return Text("Pending", style="bold yellow")
    
    def _format_created(self, task: Task) -> Text:
        """Format the created timestamp as relative time."""
        relative = task.relative_time()
        if relative == "now":
            return Text(relative, style="bold cyan")
        return Text(relative, style="dim")
    
    def get_selected_task_id(self) -> int | None:
        """Get the ID of the currently selected task."""
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
    
    def render(self) -> Text:
        """Render the help bar."""
        help_text = Text()
        
        commands = [
            ("j/k", "navigate"),
            ("x", "toggle"),
            ("a", "add"),
            ("e", "edit"),
            ("dd", "delete"),
            ("q", "quit"),
        ]
        
        for key, action in commands:
            help_text.append(f" {key}", style="bold #7aa2f7")
            help_text.append(f":{action} ", style="#565f89")
        
        return help_text


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

