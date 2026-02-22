# todo-mcp

**Multi-workspace task coordinator (MCP) that supports subtask hierarchies, dependencies, and dashboard views.**

This project aims to be a general-purpose task manager for developers working across many projects, conversations, or even outside of any project (e.g. personal grocery lists). It will support:

- Task dependencies with automatic blocking/unblocking
- Subtasks and parent/child completion rules
- Prevention of circular dependencies
- Dashboard summarizing all tasks across scopes
- Independent tasks outside of any project context
- Strong TDD with CI, pre-commit hooks, and githooks adapted from `todo-agent`

> This repository is brand new and evolving quickly. Commits will be made frequently with tests ensuring quality.

## Getting started

Install dev dependencies and run the tests:

```powershell
cd c:\Users\jake\dev\mcps\todo-mcp
python -m pip install -U pip
pip install -r requirements-dev.txt
python -m pytest -q
```

## Contributing

Before pushing changes, run `pre-commit` and ensure all tests pass. A `pre-push` git hook will run the test suite and can create tasks on failure.

To install the provided hooks after cloning the repository, run:

```bash
python -m todo_mcp.cli add-ci-githooks
``` 

This sets `core.hooksPath` to the `hooks/` folder so the same hooks work on other machines.

PRs are welcome! This project uses a vertical slice architecture to keep features isolated and make agent collaboration easier.