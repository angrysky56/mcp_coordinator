"""
Coordinator client for calling actual MCP servers.

This module provides the runtime communication layer between
generated tool wrappers and real MCP servers.
"""

import asyncio
from pathlib import Path
from typing import Any

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    raise ImportError(
        "MCP SDK is required. Install with: uv pip install mcp"
    )

from mcp_coordinator.discovery import ConfigLoader, MCPServerConfig


class CoordinatorClient:
    """
    Client for communicating with MCP servers at runtime.

    Maintains active connections to servers and routes tool calls.
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
                raise FileNotFoundError(
                    "Could not find MCP config. Please specify config_path."
                )

        self.config_path = Path(config_path)
        self.configs = ConfigLoader.load_from_json(config_path)
        self.sessions: dict[str, ClientSession] = {}
        self._connection_locks: dict[str, asyncio.Lock] = {}

    async def _ensure_connected(self, server_name: str) -> ClientSession:
        """
        Ensure connection to a server exists.

        Args:
            server_name: Name of server to connect to

        Returns:
            Active client session
        """
        # Thread-safe connection management
        if server_name not in self._connection_locks:
            self._connection_locks[server_name] = asyncio.Lock()

        async with self._connection_locks[server_name]:
            if server_name in self.sessions:
                return self.sessions[server_name]

            if server_name not in self.configs:
                raise ValueError(f"Server '{server_name}' not found in config")

            config = self.configs[server_name]

            # Create server parameters
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env,
            )

            # Connect and initialize
            read, write = await stdio_client(server_params).__aenter__()
            session = ClientSession(read, write)
            await session.initialize()

            self.sessions[server_name] = session
            return session

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        Call a tool on an MCP server.

        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        arguments = arguments or {}

        # Ensure connected
        session = await self._ensure_connected(server_name)

        # Call tool
        try:
            result = await session.call_tool(tool_name, arguments)
            return result.content
        except Exception as e:
            raise RuntimeError(
                f"Failed to call {tool_name} on {server_name}: {e}"
            ) from e

    async def close(self) -> None:
        """Close all server connections."""
        for session in self.sessions.values():
            try:
                # Sessions need proper cleanup
                # The stdio_client context manager handles this
                pass
            except Exception as e:
                print(f"Warning: Error closing session: {e}")

        self.sessions.clear()

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
