"""
MCP server discovery and introspection.

This module connects to MCP servers and discovers their capabilities:
- Available tools
- Tool schemas (parameters, descriptions)
- Resources
- Prompts

Used by the generator to create Python wrapper libraries.
"""

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    raise ImportError(
        "MCP SDK is required. Install with: uv pip install mcp"
    )


class MCPServerConfig:
    """Configuration for a single MCP server."""

    def __init__(
        self,
        name: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize server configuration.

        Args:
            name: Server identifier
            command: Command to launch server (e.g., 'uvx', 'python')
            args: Command arguments
            env: Environment variables
        """
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}

    @classmethod
    def from_dict(cls, name: str, config: dict[str, Any]) -> "MCPServerConfig":
        """Create config from dictionary (e.g., from JSON)."""
        return cls(
            name=name,
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {}),
        )


class ServerIntrospector:
    """Introspects MCP servers to discover capabilities."""

    def __init__(self, server_config: MCPServerConfig) -> None:
        """
        Initialize introspector for a server.

        Args:
            server_config: Server configuration
        """
        self.config = server_config
        self.tools: dict[str, dict[str, Any]] = {}
        self.resources: dict[str, dict[str, Any]] = {}
        self.prompts: dict[str, dict[str, Any]] = {}

    async def discover_tools(self) -> dict[str, Any]:
        """
        Connect to server and discover all capabilities.

        Returns:
            Dictionary with tools, resources, and prompts
        """
        # Create server parameters
        server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args,
            env=self.config.env,
        )

        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()

                    # List available tools
                    tools_result = await session.list_tools()
                    self.tools = {
                        tool.name: {
                            "name": tool.name,
                            "description": tool.description,
                            "input_schema": tool.inputSchema,
                        }
                        for tool in tools_result.tools
                    }

                    # Try to list resources (not all servers support this)
                    try:
                        resources_result = await session.list_resources()
                        self.resources = {
                            str(res.uri): {
                                "uri": str(res.uri),
                                "name": res.name,
                                "description": res.description,
                                "mime_type": res.mimeType,
                            }
                            for res in resources_result.resources
                        }
                    except Exception:
                        # Resources not supported
                        self.resources = {}

                    # Try to list prompts
                    try:
                        prompts_result = await session.list_prompts()
                        self.prompts = {
                            prompt.name: {
                                "name": prompt.name,
                                "description": prompt.description,
                                "arguments": prompt.arguments,
                            }
                            for prompt in prompts_result.prompts
                        }
                    except Exception:
                        # Prompts not supported
                        self.prompts = {}

            return {
                "name": self.config.name,
                "tools": self.tools,
                "resources": self.resources,
                "prompts": self.prompts,
            }

        except Exception as e:
            return {
                "name": self.config.name,
                "error": f"Failed to connect: {e}",
                "tools": {},
                "resources": {},
                "prompts": {},
            }


class ConfigLoader:
    """Loads MCP server configurations from various sources."""

    @staticmethod
    def load_from_json(filepath: str | Path) -> dict[str, MCPServerConfig]:
        """
        Load server configs from JSON file.

        Expected format:
        {
          "mcpServers": {
            "server_name": {
              "command": "uvx",
              "args": ["server-package"],
              "env": {"KEY": "value"}
            }
          }
        }

        Args:
            filepath: Path to JSON configuration file

        Returns:
            Dictionary mapping server names to configurations
        """
        filepath = Path(filepath).expanduser()

        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath) as f:
            data = json.load(f)

        servers = data.get("mcpServers", {})

        return {
            name: MCPServerConfig.from_dict(name, config)
            for name, config in servers.items()
        }


async def discover_all_servers(
    config_path: str | Path,
) -> dict[str, dict[str, Any]]:
    """
    Discover capabilities of all configured servers.

    Args:
        config_path: Path to config file (required)

    Returns:
        Dictionary mapping server names to their capabilities
    """
    # Load configuration
    configs = ConfigLoader.load_from_json(config_path)

    # Discover each server
    results = {}

    for name, config in configs.items():
        introspector = ServerIntrospector(config)
        results[name] = await introspector.discover_tools()

    return results


def discover_tools(config_path: str | Path) -> dict[str, list[str]]:
    """
    Synchronous wrapper to get tool names for all servers.

    Args:
        config_path: Path to config file (required)

    Returns:
        Dictionary mapping server names to tool name lists
    """
    results = asyncio.run(discover_all_servers(config_path))

    return {
        name: list(info["tools"].keys())
        for name, info in results.items()
        if "error" not in info
    }


def get_server_details(
    server_name: str,
    config_path: str | Path,
) -> dict[str, Any]:
    """
    Get detailed information about a specific server.

    Args:
        server_name: Name of the server
        config_path: Path to config file (required)

    Returns:
        Server capabilities dictionary
    """
    results = asyncio.run(discover_all_servers(config_path))

    if server_name not in results:
        raise ValueError(f"Server '{server_name}' not found in config")

    return results[server_name]
