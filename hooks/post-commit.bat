@echo off
REM Run tests after each commit and notify for deployment
python -m pytest -q
if %ERRORLEVEL% equ 0 (
    echo [hook] tests passed, MCP server changes are ready
) else (
    echo [hook] tests failed (exit %ERRORLEVEL%)
)
exit /b %ERRORLEVEL%
