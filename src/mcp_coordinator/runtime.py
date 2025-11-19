"""
Runtime module - provides global call_mcp_tool function for generated wrappers.

This module maintains a singleton CoordinatorClient instance that is shared
across all generated tool wrappers, enabling them to call MCP servers.
"""

from pathlib import Path
from typing import Any

from mcp_coordinator.coordinator_client import CoordinatorClient

# Global client instance (lazily initialized)
_global_client: CoordinatorClient | None = None
_config_path: str | Path | None = None


def initialize_runtime(config_path: str | Path | None = None) -> None:
    """
    Initialize the global MCP runtime client.

    This should be called once at startup, typically by Coordinator.generate_tools()
    or manually if using the generated tools directly.

    Args:
        config_path: Path to MCP server configuration
    """
    global _global_client, _config_path
    _config_path = config_path
    _global_client = CoordinatorClient(config_path)


def get_global_client() -> CoordinatorClient:
    """
    Get or create the global client instance.

    Returns:
        Shared CoordinatorClient instance

    Raises:
        RuntimeError: If runtime not initialized
    """
    global _global_client, _config_path

    if _global_client is None:
        # Auto-initialize with default config discovery
        _global_client = CoordinatorClient(_config_path)

    return _global_client


async def call_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> Any:
    """
    Call an MCP tool through the global client.

    This function is imported by all generated tool wrappers and provides
    the actual MCP communication layer.

    Args:
        server_name: Name of the MCP server
        tool_name: Name of the tool to call
        arguments: Tool arguments dictionary

    Returns:
        Tool execution result

    Example:
        >>> # Generated tools call this internally:
        >>> result = await call_mcp_tool(
        ...     server_name="chroma",
        ...     tool_name="query",
        ...     arguments={"collection": "papers", "query_text": "transformers"}
        ... )
    """
    client = get_global_client()
    return await client.call_tool(server_name, tool_name, arguments)


async def close_runtime() -> None:
    """
    Close the global runtime client and clean up resources.

    Call this when shutting down your application.
    """
    global _global_client

    if _global_client is not None:
        await _global_client.close()
        _global_client = None
