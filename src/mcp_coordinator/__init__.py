"""
MCP-Coordinator: Universal Code Execution Framework for MCP Servers.

Transforms your MCP servers into importable Python libraries,
implementing Anthropic's progressive disclosure pattern.

Quick Start:
    >>> from mcp_coordinator import Coordinator
    >>> import asyncio
    >>>
    >>> async def main():
    ...     coordinator = Coordinator("~/.config/claude/mcp_servers.json")
    ...     await coordinator.generate_tools()
    ...
    ...     # Now import and use your tools
    ...     from mcp_tools.chroma import query
    ...     results = await query(collection="papers", query_text="transformers")
    ...     print(results)
    >>>
    >>> asyncio.run(main())

For more information: https://github.com/mcp-community/mcp-coordinator
"""

__version__ = "0.1.0"
__author__ = "MCP Community"
__license__ = "MIT"

# Public API exports
from mcp_coordinator.coordinator import Coordinator, quick_coordinator
from mcp_coordinator.coordinator_client import CoordinatorClient
from mcp_coordinator.database import DatabaseManager, get_db_manager
from mcp_coordinator.discovery import (
    ConfigLoader,
    discover_all_servers,
    discover_tools,
    get_server_details,
)
from mcp_coordinator.executor import ExecutionEnvironment, SecureExecutor
from mcp_coordinator.generator import ToolGenerator, generate_from_config
from mcp_coordinator.runtime import (
    call_mcp_tool,
    close_runtime,
    initialize_runtime,
)
from mcp_coordinator.skills import SkillsManager, get_skills_manager

__all__ = [
    # Main interface
    "Coordinator",
    "quick_coordinator",

    # Execution
    "SecureExecutor",
    "ExecutionEnvironment",

    # Discovery
    "discover_all_servers",
    "discover_tools",
    "get_server_details",
    "ConfigLoader",

    # Generation
    "ToolGenerator",
    "generate_from_config",

    # Runtime
    "CoordinatorClient",
    "initialize_runtime",
    "call_mcp_tool",
    "close_runtime",

    # Skills
    "SkillsManager",
    "get_skills_manager",

    # Database
    "DatabaseManager",
    "get_db_manager",

    # Metadata
    "__version__",
]
