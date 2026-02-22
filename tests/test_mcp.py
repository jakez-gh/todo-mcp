import os
import json
import subprocess
import sys
from pathlib import Path

import pytest

from todo_mcp import mcp
from todo_mcp import mcp_tools
from todo_mcp.storage import FileStorage


def test_tool_registration():
    # at least create_task should be registered
    names = [t.name for t in mcp.list_tools()]
    assert "create_task" in names
    assert "get_ready_tasks" in names


def test_cli_create(tmp_path, capsys, monkeypatch):
    storage_file = tmp_path / "cli.json"
    mcp_tools._storage = FileStorage(storage_file)
    # invoke CLI to create a task
    monkeypatch.setattr(sys, "argv", ["todo-mcp", "create", "c1", "CliTask"])
    ret = mcp_tools  # dummy to keep flake happy
    from todo_mcp.cli import main

    main()
    captured = capsys.readouterr().out
    assert "Created task c1" in captured
    # verify via mcp tool
    ready = mcp.call_tool("get_ready_tasks", {})
    assert "c1" in ready


def test_calling_tools(tmp_path, capsys):
    # ensure storage is isolated
    storage_file = tmp_path / "tasks.json"
    # monkeypatch the storage path
    mcp_tools._storage = FileStorage(storage_file)

    # create a task
    res = mcp.call_tool("create_task", {"task_id": "x", "title": "X"})
    assert res["task_id"] == "x"
    # ready tasks should include x
    ready = mcp.call_tool("get_ready_tasks", {})
    assert "x" in ready
    # add another task depending on x
    mcp.call_tool("create_task", {"task_id": "y", "title": "Y", "depends_on": ["x"]})
    ready2 = mcp.call_tool("get_ready_tasks", {})
    assert "y" not in ready2
    # mark x complete
    mcp.call_tool("mark_task_complete", {"task_id": "x"})
    ready3 = mcp.call_tool("get_ready_tasks", {})
    assert "y" in ready3
    # status query
    status = mcp.call_tool("get_task_status", {"task_id": "y"})
    assert status["status"] == "READY"
    # ensure prints emitted
    captured = capsys.readouterr().out
    assert "[MCP] created task x" in captured


def test_stdin_server(tmp_path):
    # run the internal serve_stdin loop using StringIO so we don't have to spawn
    # a subprocess and can easily inspect the registry.
    from io import StringIO

    storage_file = tmp_path / "tasks2.json"
    mcp_tools._storage = FileStorage(storage_file)

    input_data = []
    input_data.append(json.dumps({"tool": "create_task", "input": {"task_id": "a", "title": "A"}}))
    input_data.append(json.dumps({"tool": "get_ready_tasks", "input": {}}))
    in_stream = StringIO("\n".join(input_data) + "\n")
    out_stream = StringIO()

    # run the server; it will write an initial info line and two responses
    mcp.serve_stdin(stdout=out_stream, stdin=in_stream)
    out_stream.seek(0)
    lines = [line.strip() for line in out_stream if line.strip()]
    # first line should be info listing
    info = json.loads(lines[0])
    assert info.get("info") == "tools"
    assert "create_task" in info.get("names", [])
    r1 = json.loads(lines[1])
    r2 = json.loads(lines[2])
    assert r1.get("result", {}).get("task_id") == "a"
    assert "a" in r2.get("result", [])
