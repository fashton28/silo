"""Task data model with JSON serialization."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json


@dataclass
class Task:
    """Represents a single todo task."""
    
    id: int
    title: str
    status: str = "pending"  # "pending" or "completed"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
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
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at"),
        )
    
    def relative_time(self) -> str:
        """Get human-readable relative time since creation."""
        created = datetime.fromisoformat(self.created_at)
        now = datetime.now()
        delta = now - created
        
        seconds = int(delta.total_seconds())
        
        if seconds < 60:
            return "now"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days}d"
        else:
            weeks = seconds // 604800
            return f"{weeks}w"

