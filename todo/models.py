"""Task and Workspace data models with JSON serialization."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json


@dataclass
class Workspace:
    """Represents a workspace for organizing tasks."""
    
    id: int
    name: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert workspace to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Workspace":
        """Create workspace from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data.get("created_at", datetime.now().isoformat()),
        )


@dataclass
class Task:
    """Represents a single todo task."""
    
    id: int
    title: str
    workspace_id: Optional[int] = None  # None means unassigned/legacy task
    status: str = "pending"  # "pending" or "completed"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    priority: Optional[str] = None  # "high", "medium", "low", or None
    
    def toggle(self) -> None:
        """Toggle task between pending and completed."""
        if self.status == "pending":
            self.status = "completed"
            self.completed_at = datetime.now().isoformat()
        else:
            self.status = "pending"
            self.completed_at = None
    
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == "completed"
    
    def cycle_priority(self) -> None:
        """Cycle through priority levels: None -> Low -> Medium -> High -> None."""
        cycle = [None, "low", "medium", "high"]
        current_index = cycle.index(self.priority) if self.priority in cycle else 0
        next_index = (current_index + 1) % len(cycle)
        self.priority = cycle[next_index]
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            workspace_id=data.get("workspace_id"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at"),
            priority=data.get("priority"),
        )
    
    def formatted_date(self) -> str:
        """Get the creation date formatted as date only."""
        created = datetime.fromisoformat(self.created_at)
        return created.strftime("%Y-%m-%d")

