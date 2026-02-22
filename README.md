# todo-mcp

**Multi-workspace task coordinator (MCP) that supports subtask hierarchies, dependencies, and dashboard views.**

This project started as a fork of the `todo-agent` repository (which provided a
full-featured CLI, MCP server, and storage implementation) so we could
enhance and adapt it to a multi-workspace context. The initial code in this
repo was copied over and then progressively simplified and rebuilt via vertical
slices. The goal remains: a general-purpose task manager for developers
working across many projects, conversations, or even outside of any project
(e.g. personal grocery lists). It will support:

- Task dependencies with automatic blocking/unblocking
- Subtasks and parent/child completion rules
- Prevention of circular dependencies
- Dashboard summarizing all tasks across scopes
- Independent tasks outside of any project context
- Tasks can carry arbitrary `metadata` and `agent_context` dictionaries;
  the underlying store is a simple JSON file (`.todo-mcp/tasks.json`) which
  makes it easy to inspect, edit, or share across machines.
- Agents (including the human you) may operate on their own context or a
  shared repository-wide context.
- Strong TDD with CI, pre-commit hooks, and githooks adapted from `todo-agent`

> This repository is brand new and evolving quickly. Commits will be made frequently with tests ensuring quality.

## Getting started

This repository eats its own dogfood: the code you modify here is the same code
used to track tasks while you build it. Changes are automatically materialized
into the local MCP server whenever quality gates pass, and hooks are included to
keep development environment in sync.

1. **Clone & set up** (run once per machine):

```powershell
cd c:\Users\jake\dev\mcps\todo-mcp
python -m pip install -U pip
# install runtime dependencies as well as developer tools
pip install -r requirements.txt -r requirements-dev.txt
# install hooks and dev tools
dev\install-hooks.bat     # or `bash dev/install-hooks.bat` on *nix
```

2. **Rehydrate hooks after a fresh clone**:

```powershell
dev\rehydrate-hooks.bat
```

The two batch files serve related but distinct purposes:

* `install-hooks.bat` is intended for the initial setup on a machine.  It
  installs both runtime and development dependencies and configures git hooks.
* `rehydrate-hooks.bat` is a lightweight script you can run later (for example
  on another Windows machine or after deleting `.git` metadata) to re‑apply the
  git hook configuration without reinstalling packages.  This keeps the
  workflows simple and avoids unnecessary package reinstalls.

You could merge them, but separating the dependency installation from the hook
rehydration keeps the actions orthogonal and easier to call in different
contexts.

3. **Run tests manually when needed**:

```powershell
python -m pytest -q
```

The git `post-commit` hook will also run the test suite; if it succeeds, you
will see a deployment message. (Currently deployment is local only; modify the
hook to restart a running MCP service if desired.)

4. **Use the MCP CLI to interact with tasks** (you can also use the internal
server or call tools directly from Python):

```powershell
# start a simple JSON/stdin MCP server
python -m todo_mcp.cli serve
# in another terminal, send commands:
#   echo '{"tool":"create_task","input":{"task_id":"foo","title":"Foo"}}' | python -m todo_mcp.mcp
# or use the Python API:
python - <<'PY'
from todo_mcp import mcp
print(mcp.call_tool('create_task', {'task_id':'foo','title':'Foo'}))
print(mcp.call_tool('get_ready_tasks', {}))
PY
```

```


## Contributing

Before pushing changes, run `pre-commit` and ensure all tests pass. A `pre-push` git hook will run the test suite and can create tasks on failure.

To install the provided hooks after cloning the repository, run:

```bash
python -m todo_mcp.cli add-ci-githooks
```

This sets `core.hooksPath` to the `hooks/` folder so the same hooks work on other machines.

PRs are welcome! This project uses a vertical slice architecture to keep features isolated and make agent collaboration easier.
