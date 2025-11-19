"""
Main Coordinator class - the primary interface for MCP-Coordinator.

This ties together discovery, generation, execution, and runtime.
"""

from pathlib import Path
from typing import Any

from mcp_coordinator.config import ConfigManager
from mcp_coordinator.coordinator_client import CoordinatorClient
from mcp_coordinator.discovery import discover_all_servers
from mcp_coordinator.executor import ExecutionEnvironment
from mcp_coordinator.generator import ToolGenerator


class Coordinator:
    """
    Main interface for MCP-Coordinator framework.

    Provides high-level API for:
    - Discovering MCP servers
    - Generating tool libraries
    - Executing agent code
    """

    def __init__(
        self,
        config_path: str | Path | None = None,
        tools_output_dir: str | Path = "./mcp_tools",
        workspace_dir: str | Path = "./workspace",
        project_root: str | Path | None = None,
    ) -> None:
        """
        Initialize MCP-Coordinator.

        Args:
            config_path: Path to MCP server config (uses ConfigManager resolution if None)
            tools_output_dir: Where to generate tool wrappers
            workspace_dir: Where code execution happens
            project_root: Root directory of the project (defaults to cwd)
        """
        # Initialize configuration manager
        self.config_manager = ConfigManager(
            Path(project_root) if project_root else None
        )

        # Resolve config path using priority order:
        # 1. Explicit config_path parameter
        # 2. MCP_JSON environment variable
        # 3. ./mcp_servers.json in project root
        self.config_path = self.config_manager.get_config_path(config_path)

        self.tools_output_dir = Path(tools_output_dir)
        self.workspace_dir = Path(workspace_dir)

        # Initialize components
        self.generator = ToolGenerator(self.tools_output_dir)
        self.executor_env = ExecutionEnvironment()
        self.client = CoordinatorClient(self.config_path)

        # Cached server info
        self._servers_info: dict[str, dict[str, Any]] | None = None

    async def discover_servers(self, force_refresh: bool = False) -> dict[str, dict[str, Any]]:
        """
        Discover all configured MCP servers.

        Args:
            force_refresh: If True, re-discover even if cached

        Returns:
            Dictionary of server capabilities
        """
        if self._servers_info is None or force_refresh:
            self._servers_info = await discover_all_servers(self.config_path)

        return self._servers_info

    async def generate_tools(self, force_refresh: bool = False) -> None:
        """
        Generate Python wrapper libraries for all servers.

        Args:
            force_refresh: If True, re-discover servers first
        """
        # Discover servers
        servers_info = await self.discover_servers(force_refresh)

        # Generate wrappers
        self.generator.generate_all(servers_info)

        print(f"✓ Generated tool libraries in {self.tools_output_dir}")

    async def execute_code(
        self,
        code: str,
        executor_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute Python code in sandboxed environment.

        Args:
            code: Python code to execute
            executor_name: Optional named executor (uses default if None)

        Returns:
            Execution result dictionary
        """
        return await self.executor_env.execute(code, executor_name)

    async def execute_file(
        self,
        filepath: str | Path,
        executor_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a Python file in sandboxed environment.

        Args:
            filepath: Path to Python file
            executor_name: Optional named executor

        Returns:
            Execution result dictionary
        """
        executor = self.executor_env.get_executor(executor_name)
        return await executor.execute_file(filepath)

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        Directly call an MCP tool (bypass code generation).

        Args:
            server_name: Server name
            tool_name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        return await self.client.call_tool(server_name, tool_name, arguments)

    async def list_servers(self) -> list[str]:
        """Get list of available server names."""
        servers_info = await self.discover_servers()
        return [
            name for name, info in servers_info.items()
            if "error" not in info
        ]

    async def list_tools(self, server_name: str) -> list[str]:
        """Get list of tools for a specific server."""
        servers_info = await self.discover_servers()

        if server_name not in servers_info:
            raise ValueError(f"Server '{server_name}' not found")

        server_info = servers_info[server_name]

        if "error" in server_info:
            raise RuntimeError(f"Server error: {server_info['error']}")

        return list(server_info.get("tools", {}).keys())

    async def get_tool_schema(
        self,
        server_name: str,
        tool_name: str,
    ) -> dict[str, Any]:
        """
        Get detailed schema for a specific tool.

        Args:
            server_name: Server name
            tool_name: Tool name

        Returns:
            Tool schema dictionary
        """
        servers_info = await self.discover_servers()

        if server_name not in servers_info:
            raise ValueError(f"Server '{server_name}' not found")

        server_info = servers_info[server_name]
        tools = server_info.get("tools", {})

        if tool_name not in tools:
            raise ValueError(
                f"Tool '{tool_name}' not found in server '{server_name}'"
            )

        return tools[tool_name]

    async def close(self) -> None:
        """Clean up resources."""
        await self.client.close()

    async def __aenter__(self) -> "Coordinator":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()


# Convenience function for quick setup
async def quick_coordinator(
    config_path: str | Path | None = None,
    generate: bool = True,
    project_root: str | Path | None = None,
) -> Coordinator:
    """
    Quick setup helper function.

    Args:
        config_path: Path to config (uses ConfigManager resolution if None)
        generate: If True, generates tool libraries immediately
        project_root: Root directory of the project (defaults to cwd)

    Returns:
        Initialized Coordinator instance
    """
    coordinator = Coordinator(
        config_path=config_path,
        project_root=project_root
    )

    if generate:
        await coordinator.generate_tools()

    return coordinator
