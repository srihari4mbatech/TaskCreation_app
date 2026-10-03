"""Task data model."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class Status(StrEnum):
    """Lifecycle state of a task."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Priority(StrEnum):
    """Task priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    """A single task stored in ``data/tasks.json``."""

    id: int
    title: str
    status: Status = Status.TODO
    priority: Priority = Priority.MEDIUM
    due: date | None = None
    notes: str = ""
    parent_id: int | None = Field(default=None, description="Set for subtasks.")
