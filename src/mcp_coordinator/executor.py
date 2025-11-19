"""
Secure code execution using HuggingFace's LocalPythonExecutor.

This module provides a sandboxed Python runtime that:
- Runs agent-generated code safely
- Limits allowed imports and operations
- Enforces resource constraints
- Provides transparent error handling
"""

import asyncio
import base64
import resource
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from smolagents import LocalPythonExecutor
except ImportError:
    raise ImportError("smolagents is required for secure execution. Install with: uv pip install smolagents")


def set_limits(max_cpu_time: int, max_memory: int) -> None:
    """Set resource limits for the current process."""
    if sys.platform != "win32":
        # Set CPU time limit
        resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_time, max_cpu_time))
        # Set memory limit
        resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))


class SecureExecutor:
    """
    Secure code execution environment using LocalPythonExecutor.

    Provides isolation and safety guardrails for agent-generated code
    while maintaining access to MCP tool libraries.
    """

    def __init__(
        self,
        workspace_dir: str | Path = "./workspace",
        allowed_imports: list[str] | None = None,
        denied_imports: list[str] | None = None,
        max_execution_time: float = 30.0,
        network_isolation: bool = False,
        max_cpu_time: int = 10,  # in seconds
        max_memory: int = 100 * 1024 * 1024,  # 100 MB
    ) -> None:
        """
        Initialize secure executor.

        Args:
            workspace_dir: Directory for code execution and file I/O
            allowed_imports: Whitelist of allowed import modules
            denied_imports: Blacklist of denied import modules
            max_execution_time: Maximum execution time in seconds
            network_isolation: If True, execute in a network-isolated environment
            max_cpu_time: Maximum CPU time in seconds
            max_memory: Maximum memory in bytes
        """
        self.workspace_dir = Path(workspace_dir).resolve()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.allowed_imports = allowed_imports or [
            "mcp_tools",
            "skills",
            "json",
            "csv",
            "datetime",
            "math",
            "statistics",
            "collections",
            "itertools",
            "functools",
            "pathlib",
            "typing",
        ]
        self.denied_imports = denied_imports or [
            "os",
            "subprocess",
            "sys",
            "eval",
            "exec",
            "compile",
            "__import__",
        ]
        self.max_execution_time = max_execution_time
        self.network_isolation = network_isolation
        self.max_cpu_time = max_cpu_time
        self.max_memory = max_memory
        self._setup_import_paths()
        self.executor = LocalPythonExecutor(additional_authorized_imports=self.allowed_imports)

    def _setup_import_paths(self) -> None:
        """Add necessary paths to Python import system."""
        project_root = Path(__file__).parent.parent.parent
        paths_to_add = [str(project_root), str(self.workspace_dir)]
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)

    async def _execute_isolated(self, code: str) -> dict[str, Any]:
        """Execute code in a network-isolated environment."""
        encoded_code = base64.b64encode(code.encode("utf-8")).decode("utf-8")
        helper_path = Path(__file__).parent / "_executor_helper.py"

        cmd = ["unshare", "--net", sys.executable, str(helper_path), encoded_code]

        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=lambda: set_limits(self.max_cpu_time, self.max_memory) if sys.platform != "win32" else None,
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), self.max_execution_time)

            if process.returncode == 0:
                return {
                    "success": True,
                    "result": stdout.decode().strip(),
                    "stdout": stdout.decode(),
                    "stderr": "",
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "result": None,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "error": f"Execution failed with exit code {process.returncode}",
                }
        except TimeoutError:
            if process is not None:
                try:
                    process.kill()
                except Exception:
                    pass
            return {
                "success": False,
                "result": None,
                "stdout": "",
                "stderr": "Execution timed out",
                "error": "TimeoutError: Execution exceeded the time limit.",
            }
        except FileNotFoundError:
            return {
                "success": False,
                "result": None,
                "stdout": "",
                "stderr": "The 'unshare' command was not found. Please install 'util-linux'.",
                "error": "FileNotFoundError: 'unshare' command not found.",
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "stdout": "",
                "stderr": str(e),
                "error": f"{type(e).__name__}: {e}",
            }

    async def execute(
        self,
        code: str,
        globals_dict: dict[str, Any] | None = None,
        locals_dict: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute code in sandboxed environment.
        """
        if self.network_isolation:
            return await self._execute_isolated(code)

        try:
            result = await asyncio.to_thread(self.executor.execute, code)
            return {
                "success": True,
                "result": result,
                "stdout": "",
                "stderr": "",
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "stdout": "",
                "stderr": str(e),
                "error": f"{type(e).__name__}: {e}",
            }

    async def execute_file(self, filepath: str | Path) -> dict[str, Any]:
        """
        Execute a Python file in the sandboxed environment.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return {"success": False, "error": f"File not found: {filepath}"}

        try:
            code = await asyncio.to_thread(filepath.read_text)
            return await self.execute(code)
        except Exception as e:
            return {"success": False, "error": f"Failed to read file: {e}"}

    def validate_code(self, code: str) -> tuple[bool, str | None]:
        """
        Validate code without executing it.
        """
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

        for denied in self.denied_imports:
            if f"import {denied}" in code or f"from {denied}" in code:
                return False, f"Forbidden import: {denied}"

        return True, None

    def get_available_tools(self) -> dict[str, list[str]]:
        """
        Get list of available MCP tools that can be imported.
        """
        from mcp_coordinator.discovery import discover_tools

        return discover_tools()


class ExecutionEnvironment:
    """
    High-level execution environment that manages multiple executors.
    """

    def __init__(self) -> None:
        """Initialize execution environment manager."""
        self.executors: dict[str, SecureExecutor] = {}
        self.default_executor_name = "default"
        self.executors[self.default_executor_name] = SecureExecutor()

    def create_executor(
        self,
        name: str,
        **executor_kwargs: Any,
    ) -> SecureExecutor:
        """
        Create a named executor with specific configuration.
        """
        self.executors[name] = SecureExecutor(**executor_kwargs)
        return self.executors[name]

    def get_executor(self, name: str | None = None) -> SecureExecutor:
        """
        Get an executor by name.
        """
        name = name or self.default_executor_name
        if name not in self.executors:
            raise ValueError(f"Executor '{name}' not found")
        return self.executors[name]

    async def execute(
        self,
        code: str,
        executor_name: str | None = None,
        **execute_kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute code in a named executor.
        """
        executor = self.get_executor(executor_name)
        return await executor.execute(code, **execute_kwargs)
