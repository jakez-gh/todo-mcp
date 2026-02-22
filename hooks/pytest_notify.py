#!/usr/bin/env python
"""Run pytest and create a todo-mcp task when tests fail (used by pre-push).

This script mirrors the one from todo-agent but points at the new package.
"""

import subprocess
import sys
import datetime

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
# Per-test default timeout (seconds) for pytest-timeout plugin; can be overridden per-test
DEFAULT_PYTEST_TIMEOUT = 5
# Backup timeout (seconds) to kill the whole pytest process if it hangs
BACKUP_TIMEOUT_FULL_SUITE = 900  # 15 minutes for the full suite
BACKUP_TIMEOUT_UNIT_SUITE = 120  # 2 minutes for the fast/unit subset

UNIT_PYTEST_CMD = [sys.executable, "-m", "pytest", "-q", "-m", "not integration"]
FULL_PYTEST_CMD = [sys.executable, "-m", "pytest", "-q"]

# Health check used to detect whether services are up (if applicable)
SERVICE_HEALTH_URLS = ["http://localhost:8000/health"]


def _is_service_up(url: str, timeout: int = 2) -> bool:
    import requests

    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def _try_start_services(repo_root: Path, timeout: int = 60) -> bool:
    """Try to start services automatically (Makefile / docker-compose). Returns True if services appear healthy."""
    # Prefer 'make docker-up' if Makefile exists
    if (repo_root / "Makefile").exists():
        try:
            subprocess.run(
                ["make", "docker-up"],
                cwd=str(repo_root),
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except Exception:
            pass

    # Fallback to docker-compose if present
    if (repo_root / "docker-compose.yml").exists() or (
        repo_root / "docker-compose.yaml"
    ).exists():
        try:
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=str(repo_root),
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except Exception:
            pass

    # Wait for health endpoints
    deadline = datetime.datetime.utcnow().timestamp() + timeout
    for url in SERVICE_HEALTH_URLS:
        while datetime.datetime.utcnow().timestamp() < deadline:
            if _is_service_up(url):
                break
            time.sleep(1)
        else:
            return False
    return True


def _create_todo_for_failure(repo_root: Path, title: str, snippet: str) -> None:
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    task_id = f"ci-failure-{timestamp}"
    description = f"Automated pre-push failure detected.\n\n{snippet[:4000]}"
    create_cmd = [
        sys.executable,
        "-m",
        "todo_mcp.cli",
        "create",
        task_id,
        title,
        "--description",
        description,
    ]
    try:
        subprocess.run(create_cmd, cwd=str(repo_root), check=True)
        print(f"Created todo-mcp task: {task_id}")
    except Exception as e:
        print(f"Failed to create todo-mcp task: {e}")


def main() -> int:

    # 1) Run pre-commit checks (auto-fix where possible)
    print("Running pre-commit checks (auto-fix)...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pre_commit", "run", "--all-files"],
            cwd=str(REPO_ROOT),
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print("Pre-commit checks failed. Fix issues and try again.")
        return e.returncode

    # 2) Run fast/unit tests first
    print("Running fast/unit test subset...")
    try:
        proc = subprocess.run(
            UNIT_PYTEST_CMD,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=BACKUP_TIMEOUT_UNIT_SUITE,
        )
    except subprocess.TimeoutExpired:
        snippet = "Unit test run timed out (backup timeout)"
        _create_todo_for_failure(REPO_ROOT, "Unit tests timed out (pre-push)", snippet)
        print(snippet)
        return 124

    if proc.returncode != 0:
        snippet = proc.stdout + "\n" + proc.stderr
        _create_todo_for_failure(REPO_ROOT, "Unit tests failed (pre-push)", snippet)
        print("Unit tests failed — push blocked; created task for investigation.")
        return proc.returncode

    print("Unit tests passed. Proceeding to full test suite...")

    # 3) Ensure required services are running (try to start them if not)
    need_start = False
    for url in SERVICE_HEALTH_URLS:
        if not _is_service_up(url):
            need_start = True
            break
    if need_start:
        print(
            "Detected services are not running. Attempting to start common services (docker/make)..."
        )
        started = _try_start_services(REPO_ROOT, timeout=60)
        if not started:
            msg = (
                "Could not start services automatically.\n"
                "Please start required services (e.g. `make docker-up` or `docker-compose up -d`) and re-run the push."
            )
            print(msg)
            _create_todo_for_failure(
                REPO_ROOT, "Services not running for test suite (pre-push)", msg
            )
            return 125
        print("Services reportedly started and healthy.")

    # 4) Run full pytest suite with a backup timeout
    print("Running full test suite (this may take a while)...")
    try:
        proc = subprocess.run(
            FULL_PYTEST_CMD,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=BACKUP_TIMEOUT_FULL_SUITE,
        )
    except subprocess.TimeoutExpired:
        snippet = "Full test suite timed out (backup timeout)"
        _create_todo_for_failure(
            REPO_ROOT, "Full test suite timed out (pre-push)", snippet
        )
        print(snippet)
        return 124

    if proc.returncode == 0:
        print("All tests passed — pre-push checks complete.")
        return 0

    # Tests failed — create a todo-mcp task so MCP-connected agents are notified
    short_output = proc.stdout + "\n" + proc.stderr
    snippet = short_output[:4000]
    _create_todo_for_failure(REPO_ROOT, "CI test failures (pre-push)", snippet)

    print("Full tests failed — push blocked; created task for investigation.")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())