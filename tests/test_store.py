from __future__ import annotations

from pathlib import Path

from taskmgr.models import Priority, Status, Task
from taskmgr.store import TaskStore


def make_store(tmp_path: Path) -> TaskStore:
    return TaskStore(tmp_path / "tasks.json")


def test_creates_empty_file(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    assert store.path.read_text().strip() == "[]"
    assert store.list_tasks() == []


def test_add_assigns_incrementing_ids(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    first = store.add(Task(id=0, title="a"))
    second = store.add(Task(id=0, title="b"))
    assert (first.id, second.id) == (1, 2)


def test_update_and_delete(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    task = store.add(Task(id=0, title="a"))
    updated = store.update(task.id, status=Status.DONE, priority=Priority.HIGH)
    assert updated is not None
    assert updated.status is Status.DONE
    assert store.update(99, title="x") is None
    assert store.delete(task.id) is True
    assert store.delete(task.id) is False


def test_corrupted_file_returns_empty(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.path.write_text("not json")
    assert store.list_tasks() == []


def test_invalid_entries_are_skipped(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.path.write_text('[{"id": 1, "title": "ok"}, {"bad": true}]')
    assert [t.title for t in store.list_tasks()] == ["ok"]
