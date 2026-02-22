@echo off
REM Re-apply git hooks configuration (useful on a fresh clone or after cloning on another machine)
python -m todo_mcp.cli add-ci-githooks
pre-commit install
ECHO Hooks rehydrated.
