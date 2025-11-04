"""Local Python execution tool for AP WRIMS analysis agents."""

from __future__ import annotations

import io
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import Any, Dict


_EXEC_GLOBALS: Dict[str, Any] = {}


def run_python_code(code: str) -> dict:
    """Executes Python code in a persistent local namespace.

    Args:
        code: The Python source to execute.

    Returns:
        dict with keys:
            status: 'success' or 'error'
            code: dedented code that was executed
            stdout: captured stdout from execution
            error: optional error string if execution failed
    """

    dedented = textwrap.dedent(code).strip()
    stdout_buffer = io.StringIO()

    try:
        with redirect_stdout(stdout_buffer):
            exec(dedented, _EXEC_GLOBALS, _EXEC_GLOBALS)
    except Exception:
        return {
            "status": "error",
            "code": dedented,
            "stdout": stdout_buffer.getvalue(),
            "error": traceback.format_exc(),
        }

    return {
        "status": "success",
        "code": dedented,
        "stdout": stdout_buffer.getvalue(),
    }

