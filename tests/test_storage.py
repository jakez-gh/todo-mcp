import os
import json
from pathlib import Path

import pytest

from todo_mcp.tasks import Task, TaskManager, Status
from todo_mcp.storage import FileStorage


def test_storage_roundtrip(tmp_path):
    storage_file = tmp_path / "store.json"
    storage = FileStorage(storage_file)
    mgr = TaskManager()
    mgr.add_task(Task(id="a", title="A"))
    mgr.add_task(Task(id="b", title="B"))
    mgr.add_dependency("b", "a")
    mgr.tasks["a"].metadata["foo"] = "bar"
    storage.save(mgr)

    # ensure file exists and contains JSON
    assert storage_file.exists()
    data = json.loads(storage_file.read_text())
    assert "a" in data and "b" in data

    # load back
    mgr2 = storage.load()
    assert mgr2.tasks["a"].title == "A"
    assert mgr2.tasks["b"].dependencies == {"a"}
    assert mgr2.tasks["a"].metadata.get("foo") == "bar"
