"""Command-line interface for todo-mcp."""

import argparse
import sys
import json

from .tasks import TaskManager, Task
from . import mcp
from . import mcp_tools  # ensure tools registered


def add_ci_githooks():
    """Install repository githooks by setting `core.hooksPath` to `hooks`.

    This mirrors the behavior in todo-agent and ensures clones on other
    machines will use the provided hooks directory.
    """
    from pathlib import Path
    import subprocess

    repo_root = Path(__file__).resolve().parents[1]
    hooks_dir = repo_root / "hooks"
    if not hooks_dir.exists():
        print(f"Error: hooks directory not found at {hooks_dir}")
        return 1

    try:
        subprocess.run(
            ["git", "config", "core.hooksPath", "hooks"],
            cwd=str(repo_root),
            check=True,
        )
    except Exception as exc:
        print(f"Error setting git config core.hooksPath: {exc}")
        return 1

    try:
        for p in hooks_dir.iterdir():
            if p.is_file():
                try:
                    p.chmod(p.stat().st_mode | 0o111)
                except Exception:
                    pass
    except Exception:
        pass

    print("✓ Installed git hooks (core.hooksPath -> hooks)")
    return 0


def main():
    parser = argparse.ArgumentParser(prog="todo-mcp")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("id")
    create_parser.add_argument("title")
    create_parser.add_argument("--metadata", help="JSON metadata for the task")
    create_parser.add_argument("--depends-on", action="append", help="Dependencies")

    subparsers.add_parser("tasks", help="Show dashboard of all tasks")

    subparsers.add_parser("serve", help="Start MCP stdin/stdout server")

    subparsers.add_parser("add-ci-githooks", help="Install git hooks from hooks/")

    args = parser.parse_args()
    if args.command == "create":
        payload = {"task_id": args.id, "title": args.title}
        if args.metadata:
            try:
                payload["metadata"] = json.loads(args.metadata)
            except Exception:
                print("Error: metadata must be valid JSON")
                return 1
        if args.depends_on:
            payload["depends_on"] = args.depends_on
        res = mcp.call_tool("create_task", payload)
        print(f"Created task {res['task_id']}")
        return 0
    elif args.command == "tasks":
        tasks = mcp.call_tool("list_tasks", {})
        for t in tasks:
            print(f"{t['id']}  [{t['status']}] {t['title']}")
        return 0
    elif args.command == "serve":
        print("Starting MCP server (type JSON lines to interact)")
        mcp.serve_stdin()
        return 0
    elif args.command == "add-ci-githooks":
        return add_ci_githooks()
    else:
        parser.print_help()
        sys.exit(1)
