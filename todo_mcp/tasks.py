"""Core task management for todo-mcp."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Set


class Status(Enum):
    PENDING = auto()
    READY = auto()
    BLOCKED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()


@dataclass
class Task:
    id: str
    title: str
    status: Status = Status.PENDING
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    parent: str | None = None  # optional parent task id
    subtasks: Set[str] = field(default_factory=set)


class CircularDependencyError(Exception):
    pass


class TaskNotFoundError(KeyError):
    pass


class TaskManager:
    """Simple in-memory task manager with dependency handling."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add_task(self, task: Task) -> None:
        if task.id in self.tasks:
            raise KeyError(f"Task with id '{task.id}' already exists")
        self.tasks[task.id] = task
        self._update_status(task)

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        task = self._get(task_id)
        other = self._get(depends_on)
        # prevent circular
        if self._creates_cycle(task_id, depends_on):
            raise CircularDependencyError(f"Adding dependency {task_id} -> {depends_on} would create a cycle")
        task.dependencies.add(depends_on)
        other.dependents.add(task_id)
        self._update_status(task)

    def mark_complete(self, task_id: str) -> None:
        task = self._get(task_id)
        task.status = Status.COMPLETED
        # propagate to dependents
        for dep_id in task.dependents:
            self._update_status(self.tasks[dep_id])
        # propagate to parent
        if task.parent:
            parent = self._get(task.parent)
            # if all subtasks complete, mark parent complete
            if all(self.tasks[sub].status == Status.COMPLETED for sub in parent.subtasks):
                parent.status = Status.COMPLETED

    def _get(self, task_id: str) -> Task:
        try:
            return self.tasks[task_id]
        except KeyError:
            raise TaskNotFoundError(task_id)

    def _update_status(self, task: Task) -> None:
        # if already completed, leave it
        if task.status == Status.COMPLETED:
            return
        if task.dependencies and any(self.tasks[d].status != Status.COMPLETED for d in task.dependencies):
            task.status = Status.BLOCKED
        else:
            task.status = Status.READY

    def _creates_cycle(self, start: str, depends_on: str) -> bool:
        # DFS from depends_on to see if we can reach start
        visited = set()
        stack = [depends_on]
        while stack:
            cur = stack.pop()
            if cur == start:
                return True
            if cur in visited:
                continue
            visited.add(cur)
            stack.extend(self.tasks[cur].dependencies)
        return False

    # extras for parent/subtask
    def add_subtask(self, parent_id: str, subtask_id: str) -> None:
        parent = self._get(parent_id)
        sub = self._get(subtask_id)
        parent.subtasks.add(subtask_id)
        sub.parent = parent_id
        # parent shouldn't be marked complete until subtasks done
        self._update_status(parent)

    def get_ready_tasks(self) -> List[Task]:
        return [t for t in self.tasks.values() if t.status == Status.READY]
