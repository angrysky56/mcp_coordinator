"""Coordinator client for calling actual MCP servers.

This module provides the runtime communication layer between
generated tool wrappers and real MCP servers, using the robust
McpClientManager for connection management.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from mcp_coordinator.core import McpClientManager

logger = logging.getLogger("mcp_coordinator.client")


class CoordinatorClient:
    """
    Client for communicating with MCP servers at runtime.

    Wraps McpClientManager to provide a simple interface for tool execution.
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """
        Initialize coordinator client.

        Args:
            config_path: Path to MCP server configuration
        """
        self.manager = McpClientManager()
        self.manager.initialize(Path(config_path) if config_path else None)

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
        return await self.manager.call_tool(server_name, tool_name, arguments)

    async def close(self) -> None:
        """Close all connections."""
        await self.manager.cleanup()

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
