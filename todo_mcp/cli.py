"""Command-line interface for todo-mcp."""

import argparse
import sys

from .tasks import TaskManager, Task


def main():
    parser = argparse.ArgumentParser(prog="todo-mcp")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("id")
    create_parser.add_argument("title")

    args = parser.parse_args()
    if args.command == "create":
        mgr = TaskManager()
        task = Task(id=args.id, title=args.title)
        mgr.add_task(task)
        print(f"Created task {args.id}")
    else:
        parser.print_help()
        sys.exit(1)
