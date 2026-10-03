"""JSON-file persistence for tasks."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path

from pydantic import ValidationError

from taskmgr.models import Task

logger = logging.getLogger(__name__)

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


class TaskStore:
    """Reads and writes the task list in a JSON file."""

    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        """Create the store, initialising an empty file if none exists.

        Args:
            path: Location of the JSON file.
        """
        self.path = path
        if not self.path.exists():
            self._write([])

    def list_tasks(self) -> list[Task]:
        """Return all tasks.

        Returns:
            Tasks in file order. Invalid entries are skipped and logged, and an
            unreadable file yields an empty list.
        """
        try:
            raw = json.loads(self.path.read_text())
        except (OSError, json.JSONDecodeError):
            logger.exception("Could not read %s", self.path)
            return []
        if not isinstance(raw, list):
            logger.error("%s must contain a JSON list", self.path)
            return []
        tasks: list[Task] = []
        for item in raw:
            try:
                tasks.append(Task.model_validate(item))
            except ValidationError:
                logger.warning("Skipping invalid task entry: %s", item)
        return tasks

    def add(self, task: Task) -> Task:
        """Append a task, assigning the next free ID.

        Args:
            task: Task to add. Its ``id`` is overwritten.

        Returns:
            The stored task with its new ID.
        """
        tasks = self.list_tasks()
        stored = task.model_copy(update={"id": max((t.id for t in tasks), default=0) + 1})
        self._write([*tasks, stored])
        return stored

    def update(self, task_id: int, **changes: object) -> Task | None:
        """Apply field changes to a task.

        Args:
            task_id: ID of the task to change.
            **changes: Field names and new values.

        Returns:
            The updated task, or None if no task has that ID.
        """
        tasks = self.list_tasks()
        for index, task in enumerate(tasks):
            if task.id == task_id:
                updated = Task.model_validate({**task.model_dump(), **changes})
                tasks[index] = updated
                self._write(tasks)
                return updated
        return None

    def delete(self, task_id: int) -> bool:
        """Remove a task.

        Args:
            task_id: ID of the task to remove.

        Returns:
            True if a task was removed.
        """
        tasks = self.list_tasks()
        remaining = [t for t in tasks if t.id != task_id]
        if len(remaining) == len(tasks):
            return False
        self._write(remaining)
        return True

    def _write(self, tasks: list[Task]) -> None:
        """Atomically write tasks to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps([t.model_dump(mode="json") for t in tasks], indent=2)
        fd, tmp_name = tempfile.mkstemp(dir=self.path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as handle:
                handle.write(payload)
            Path(tmp_name).replace(self.path)
        finally:
            Path(tmp_name).unlink(missing_ok=True)
