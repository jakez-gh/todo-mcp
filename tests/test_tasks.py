import pytest

from todo_mcp.tasks import Task, TaskManager, Status, CircularDependencyError


def test_add_and_complete_dependency_cycle():
    mgr = TaskManager()
    mgr.add_task(Task(id="a", title="A"))
    mgr.add_task(Task(id="b", title="B"))
    mgr.add_dependency("b", "a")
    assert mgr.tasks["a"].status == Status.READY
    assert mgr.tasks["b"].status == Status.BLOCKED

    mgr.mark_complete("a")
    assert mgr.tasks["a"].status == Status.COMPLETED
    assert mgr.tasks["b"].status == Status.READY

    # ensure cycle detection
    mgr.add_task(Task(id="c", title="C"))
    mgr.add_dependency("c", "b")
    with pytest.raises(CircularDependencyError):
        mgr.add_dependency("a", "c")


def test_subtasks_complete_parent():
    mgr = TaskManager()
    mgr.add_task(Task(id="p", title="parent"))
    mgr.add_task(Task(id="s1", title="child1"))
    mgr.add_task(Task(id="s2", title="child2"))
    mgr.add_subtask("p", "s1")
    mgr.add_subtask("p", "s2")
    # parent is ready since no dependencies on parent itself
    assert mgr.tasks["p"].status == Status.READY

    mgr.mark_complete("s1")
    assert mgr.tasks["p"].status != Status.COMPLETED
    mgr.mark_complete("s2")
    assert mgr.tasks["p"].status == Status.COMPLETED
