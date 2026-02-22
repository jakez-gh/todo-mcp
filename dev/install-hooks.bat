@echo off
REM Install git hooks for this repository and pre-commit tools.
python -m todo_mcp.cli add-ci-githooks
python -m pip install -r requirements-dev.txt


ECHO Hooks and dev deps installed.npre-commit install