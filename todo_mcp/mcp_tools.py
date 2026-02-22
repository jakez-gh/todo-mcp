"""Register task-related tools using the internal MCP registry."""

from __future__ import annotations

from typing import Any, Dict, List

from . import mcp
from .storage import FileStorage
from .tasks import Task, TaskManager, Status, CircularDependencyError, TaskNotFoundError
from pathlib import Path

# helper to load/save manager
_storage = FileStorage()


def _load_mgr() -> TaskManager:
    return _storage.load()


def _save_mgr(mgr: TaskManager) -> None:
    _storage.save(mgr)


@mcp.register_tool(
    name="create_task",
    description="Create a new task with optional metadata and dependencies",
    input_schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string"},
            "title": {"type": "string"},
            "metadata": {"type": "object"},
            "depends_on": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["task_id", "title"],
    },
)
def tool_create_task(args: Dict[str, Any]) -> Dict[str, Any]:
    mgr = _load_mgr()
    task = Task(id=args["task_id"], title=args["title"])
    task.metadata.update(args.get("metadata", {}))
    mgr.add_task(task)
    for dep in args.get("depends_on", []):
        mgr.add_dependency(task.id, dep)
    _save_mgr(mgr)
    print(f"[MCP] created task {task.id}")
    return {"task_id": task.id}


@mcp.register_tool(
    name="get_ready_tasks",
    description="Return list of task IDs currently ready",
    input_schema={"type": "object", "properties": {}},
)
def tool_get_ready(args: Dict[str, Any]) -> List[str]:
    mgr = _load_mgr()
    return [t.id for t in mgr.get_ready_tasks()]


@mcp.register_tool(
    name="add_dependency",
    description="Add a dependency between tasks",
    input_schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string"},
            "depends_on": {"type": "string"},
        },
        "required": ["task_id", "depends_on"],
    },
)
def tool_add_dependency(args: Dict[str, Any]) -> Dict[str, Any]:
    mgr = _load_mgr()
    mgr.add_dependency(args["task_id"], args["depends_on"])
    _save_mgr(mgr)
    print(f"[MCP] added dependency {args['task_id']} -> {args['depends_on']}")
    return {"task_id": args["task_id"], "depends_on": args["depends_on"]}


@mcp.register_tool(
    name="mark_task_complete",
    description="Mark a task complete",
    input_schema={
        "type": "object",
        "properties": {"task_id": {"type": "string"}},
        "required": ["task_id"],
    },
)
def tool_mark_complete(args: Dict[str, Any]) -> Dict[str, Any]:
    mgr = _load_mgr()
    mgr.mark_complete(args["task_id"])
    _save_mgr(mgr)
    print(f"[MCP] marked complete {args['task_id']}")
    return {"task_id": args["task_id"]}


@mcp.register_tool(
    name="get_task_status",
    description="Return status of a specific task",
    input_schema={
        "type": "object",
        "properties": {"task_id": {"type": "string"}},
        "required": ["task_id"],
    },
)
def tool_get_status(args: Dict[str, Any]) -> Dict[str, Any]:
    mgr = _load_mgr()
    task = mgr.tasks.get(args["task_id"])
    if not task:
        raise TaskNotFoundError(args["task_id"])
    return {"id": task.id, "status": task.status.name, "metadata": task.metadata}


# ---------------------------------------------------------------------------
# export utilities
# ---------------------------------------------------------------------------

@mcp.register_tool(
    name="export_html",
    description="Export all tasks to a simple HTML file",
    input_schema={
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    },
)
def tool_export_html(args: Dict[str, Any]) -> Dict[str, Any]:
    mgr = _load_mgr()
    path = Path(args["path"])
    rows = []
    for t in mgr.tasks.values():
        rows.append(f"<tr><td>{t.id}</td><td>{t.title}</td><td>{t.status.name}</td></tr>")
    html = """<!doctype html><html><head><meta charset=\"utf-8\"><title>Tasks</title></head><body><table border=1>"""
    html += """<tr><th>ID</th><th>Title</th><th>Status</th></tr>"""
    html += "".join(rows)
    html += "</table></body></html>"
    path.write_text(html, encoding="utf-8")
    return {"path": str(path)}


# ----- new utility tool --------------------------------------------------

@mcp.register_tool(
    name="list_tasks",
    description="Return a list of all tasks with details",
    input_schema={"type": "object", "properties": {}},
)
def tool_list_tasks(args: Dict[str, Any]) -> List[Dict[str, Any]]:
    mgr = _load_mgr()
    return [t.to_dict() for t in mgr.tasks.values()]
