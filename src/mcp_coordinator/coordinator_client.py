"""
Coordinator client for calling actual MCP servers.

This module provides the runtime communication layer between
generated tool wrappers and real MCP servers.
"""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    raise ImportError("MCP SDK is required. Install with: uv pip install mcp")

from mcp_coordinator.discovery import ConfigLoader


class CoordinatorClient:
    """
    Client for communicating with MCP servers at runtime.

    Uses fresh connections per tool call for reliability.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """
        Initialize coordinator client.

        Args:
            config_path: Path to MCP server configuration
        """
        if config_path is None:
            config_path = ConfigLoader.discover_claude_config()
            if config_path is None:
                raise FileNotFoundError("Could not find MCP config. Please specify config_path.")

        self.config_path = Path(config_path)
        self.configs = ConfigLoader.load_from_json(config_path)

    def _resolve_command(self, command: str, path_env: str | None = None) -> str:
        """Resolve command to absolute path if possible.

        Args:
            command: Command name or path
            path_env: Optional PATH environment variable

        Returns:
            Resolved absolute path or original command
        """
        # If already absolute path, return as-is
        if os.path.isabs(command):
            return command

        # Try to find in PATH
        resolved = shutil.which(command, path=path_env)
        if resolved:
            return resolved

        # Try common tool locations
        home = Path.home()
        common_paths = [
            home / ".pyenv" / "shims" / command,
            home / ".cargo" / "bin" / command,
            home / ".local" / "bin" / command,
            home / ".nvm" / "versions" / "node" / "*" / "bin" / command,
        ]

        for path in common_paths:
            if path.exists():
                return str(path)

        # Fallback to original command
        return command

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        Call a tool on an MCP server with a fresh connection.

        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        arguments = arguments or {}

        if server_name not in self.configs:
            raise ValueError(f"Server '{server_name}' not found in config")

        config = self.configs[server_name]

        # Merge with current environment to preserve PATH, etc.
        env = dict(os.environ)
        if config.env:
            env.update(config.env)

        # Ensure standard paths are in PATH
        current_path = env.get("PATH", "")
        standard_paths = ["/usr/local/bin", "/usr/bin", "/bin"]
        for p in standard_paths:
            if p not in current_path.split(os.pathsep):
                current_path = f"{current_path}{os.pathsep}{p}" if current_path else p
        env["PATH"] = current_path

        # Resolve command path
        command = self._resolve_command(config.command, env.get("PATH"))

        # Create server parameters
        server_params = StdioServerParameters(
            command=command,
            args=config.args,
            env=env,
        )

        # Create fresh connection for this call
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()

                    # Call tool
                    result = await session.call_tool(tool_name, arguments)
                    return result.content
        except Exception as e:
            raise RuntimeError(f"Failed to call {tool_name} on {server_name}: {e}") from e

    async def close(self) -> None:
        """Close - no-op with fresh connections pattern."""
        pass

    async def __aenter__(self) -> "CoordinatorClient":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()


# Global client instance for simple usage
_global_client: CoordinatorClient | None = None


async def call_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    config_path: str | Path | None = None,
) -> Any:
    """
    High-level function to call an MCP tool.

    This is the function that generated tool wrappers call.

    Args:
        server_name: Name of the server
        tool_name: Name of the tool
        arguments: Tool arguments
        config_path: Optional config path (uses global client if None)

    Returns:
        Tool execution result
    """
    global _global_client

    # Use global client for efficiency
    if _global_client is None:
        _global_client = CoordinatorClient(config_path)

    return await _global_client.call_tool(server_name, tool_name, arguments)


def cleanup_global_client() -> None:
    """Clean up global client. Call this when shutting down."""
    global _global_client

    if _global_client is not None:
        asyncio.run(_global_client.close())
        _global_client = None
