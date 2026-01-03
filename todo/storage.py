"""JSON file storage for tasks."""

import json
from pathlib import Path
from typing import List

from .models import Task


# Default storage location
DEFAULT_TODO_DIR = Path.home() / ".todo"
DEFAULT_TASKS_FILE = DEFAULT_TODO_DIR / "tasks.json"
DEFAULT_HISTORY_FILE = DEFAULT_TODO_DIR / "history.json"


def ensure_storage_exists() -> None:
    """Create storage directory and file if they don't exist."""
    DEFAULT_TODO_DIR.mkdir(parents=True, exist_ok=True)
    if not DEFAULT_TASKS_FILE.exists():
        DEFAULT_TASKS_FILE.write_text("[]")
    if not DEFAULT_HISTORY_FILE.exists():
        DEFAULT_HISTORY_FILE.write_text("[]")


def load_tasks() -> List[Task]:
    """Load all tasks from the JSON file."""
    ensure_storage_exists()
    
    try:
        data = json.loads(DEFAULT_TASKS_FILE.read_text())
        return [Task.from_dict(item) for item in data]
    except (json.JSONDecodeError, KeyError):
        return []


def save_tasks(tasks: List[Task]) -> None:
    """Save all tasks to the JSON file."""
    ensure_storage_exists()
    
    data = [task.to_dict() for task in tasks]
    DEFAULT_TASKS_FILE.write_text(json.dumps(data, indent=2))


def get_next_id(tasks: List[Task]) -> int:
    """Get the next available task ID."""
    if not tasks:
        return 1
    return max(task.id for task in tasks) + 1


def add_task(title: str) -> Task:
    """Create and save a new task."""
    tasks = load_tasks()
    new_task = Task(id=get_next_id(tasks), title=title)
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task


def delete_task(task_id: int) -> bool:
    """Delete a task by ID. Returns True if task was found and deleted."""
    tasks = load_tasks()
    original_count = len(tasks)
    tasks = [t for t in tasks if t.id != task_id]
    
    if len(tasks) < original_count:
        save_tasks(tasks)
        return True
    return False


def toggle_task(task_id: int) -> bool:
    """Toggle a task's completion status. Returns True if task was found."""
    tasks = load_tasks()
    
    for task in tasks:
        if task.id == task_id:
            task.toggle()
            save_tasks(tasks)
            return True
    return False


def update_task_title(task_id: int, new_title: str) -> bool:
    """Update a task's title. Returns True if task was found."""
    tasks = load_tasks()
    
    for task in tasks:
        if task.id == task_id:
            task.title = new_title
            save_tasks(tasks)
            return True
    return False


def cycle_task_priority(task_id: int) -> bool:
    """Cycle a task's priority. Returns True if task was found."""
    tasks = load_tasks()
    
    for task in tasks:
        if task.id == task_id:
            task.cycle_priority()
            save_tasks(tasks)
            return True
    return False


def move_task_up(task_id: int) -> bool:
    """Move a task up in the list. Returns True if moved."""
    tasks = load_tasks()
    
    for i, task in enumerate(tasks):
        if task.id == task_id:
            if i > 0:  # Can only move up if not already at top
                tasks[i], tasks[i - 1] = tasks[i - 1], tasks[i]
                save_tasks(tasks)
                return True
            return False
    return False


def move_task_down(task_id: int) -> bool:
    """Move a task down in the list. Returns True if moved."""
    tasks = load_tasks()
    
    for i, task in enumerate(tasks):
        if task.id == task_id:
            if i < len(tasks) - 1:  # Can only move down if not already at bottom
                tasks[i], tasks[i + 1] = tasks[i + 1], tasks[i]
                save_tasks(tasks)
                return True
            return False
    return False


def clear_completed() -> int:
    """Remove all completed tasks and archive them to history. Returns number of tasks archived."""
    tasks = load_tasks()
    completed = [t for t in tasks if t.is_completed()]
    remaining = [t for t in tasks if not t.is_completed()]
    
    if completed:
        # Archive completed tasks to history
        history = load_history()
        history.extend(completed)
        save_history(history)
    
    save_tasks(remaining)
    return len(completed)


# History functions

def load_history() -> List[Task]:
    """Load all tasks from the history file."""
    ensure_storage_exists()
    
    try:
        data = json.loads(DEFAULT_HISTORY_FILE.read_text())
        return [Task.from_dict(item) for item in data]
    except (json.JSONDecodeError, KeyError):
        return []


def save_history(tasks: List[Task]) -> None:
    """Save all tasks to the history file."""
    ensure_storage_exists()
    
    data = [task.to_dict() for task in tasks]
    DEFAULT_HISTORY_FILE.write_text(json.dumps(data, indent=2))


def clear_history() -> int:
    """Clear all history. Returns number of tasks removed."""
    history = load_history()
    count = len(history)
    DEFAULT_HISTORY_FILE.write_text("[]")
    return count

