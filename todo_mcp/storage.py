"""JSON-based storage for todo-mcp tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .tasks import Task, TaskManager


class FileStorage:
    """Loads and saves a TaskManager from a JSON file."""

    def __init__(self, path: Path | str | None = None):
        # default to .todo-mcp/tasks.json in current working directory
        if path is None:
            path = Path(".todo-mcp") / "tasks.json"
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> TaskManager:
        mgr = TaskManager()
        if not self.path.exists():
            return mgr
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # data expected to be dict of id->task-dict
        for tid, tdict in data.items():
            task = Task.from_dict(tdict)
            mgr.tasks[tid] = task
        return mgr

    def save(self, mgr: TaskManager) -> None:
        data: Dict[str, dict] = {}
        for tid, task in mgr.tasks.items():
            data[tid] = task.to_dict()
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
