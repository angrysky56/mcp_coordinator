#!/usr/bin/env python3
"""MCP server that exposes the coordinator's functionality as MCP tools.

This allows AI clients to add just this one server to their config instead of
duplicating all individual MCP servers.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .coordinator import Coordinator
from .executor import SecureExecutor
from .skills import get_skills_manager

# Initialize FastMCP server
mcp = FastMCP("mcp-coordinator")

# Global instances (initialized on first use)
_coordinator: Coordinator | None = None
_executor: SecureExecutor | None = None


def get_coordinator() -> Coordinator:
    """Get or create coordinator instance."""
    global _coordinator
    if _coordinator is None:
        # Initialize with default paths
        _coordinator = Coordinator()
    return _coordinator


@mcp.tool()
async def discover_servers(force_refresh: bool = False) -> dict[str, Any]:
    """Discover all configured MCP servers and their capabilities.
    
    Args:
        force_refresh: If True, re-discover even if cached
        
    Returns:
        Dictionary of server capabilities
    """
    coordinator = get_coordinator()
    return await coordinator.discover_servers(force_refresh)


@mcp.tool()
async def list_servers() -> list[str]:
    """Get list of available MCP server names.
    
    Returns:
        List of server names
    """
    coordinator = get_coordinator()
    return await coordinator.list_servers()


@mcp.tool()
async def list_tools(server_name: str) -> list[str]:
    """Get list of tools for a specific server.
    
    Args:
        server_name: Name of the server
        
    Returns:
        List of tool names for the server
    """
    coordinator = get_coordinator()
    return await coordinator.list_tools(server_name)


@mcp.tool()
async def get_tool_schema(server_name: str, tool_name: str) -> dict[str, Any]:
    """Get detailed schema for a specific tool.
    
    Args:
        server_name: Name of the server
        tool_name: Name of the tool
        
    Returns:
        Tool schema dictionary
    """
    coordinator = get_coordinator()
    return await coordinator.get_tool_schema(server_name, tool_name)


@mcp.tool()
async def call_tool(
    server_name: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None
) -> Any:
    """Call an MCP tool directly.
    
    Args:
        server_name: Name of the server
        tool_name: Name of the tool to call
        arguments: Arguments to pass to the tool
        
    Returns:
        Result from the tool execution
    """
    coordinator = get_coordinator()
    return await coordinator.call_tool(server_name, tool_name, arguments)


@mcp.tool()
async def generate_tools(force_refresh: bool = False) -> str:
    """Generate Python wrapper libraries for all MCP servers.
    
    Args:
        force_refresh: If True, re-discover servers before generating
        
    Returns:
        Success message with output directory
    """
    coordinator = get_coordinator()
    await coordinator.generate_tools(force_refresh)
    return f"✓ Generated tool libraries in {coordinator.tools_output_dir}"


@mcp.tool()
async def execute_code(
    code: str,
    executor_name: str | None = None
) -> dict[str, Any]:
    """Execute Python code in a sandboxed environment.
    
    Args:
        code: Python code to execute
        executor_name: Optional named executor (uses default if None)
        
    Returns:
        Execution result dictionary with stdout, stderr, and return value
    """
    coordinator = get_coordinator()
    return await coordinator.execute_code(code, executor_name)


@mcp.tool()
async def execute_file(
    filepath: str,
    executor_name: str | None = None
) -> dict[str, Any]:
    """Execute a Python file in a sandboxed environment.
    
    Args:
        filepath: Path to Python file to execute
        executor_name: Optional named executor (uses default if None)
        
    Returns:
        Execution result dictionary with stdout, stderr, and return value
    """
    coordinator = get_coordinator()
    return await coordinator.execute_file(Path(filepath), executor_name)


def main() -> None:
    """Entry point for the MCP coordinator server."""
    # Log to stderr as per MCP conventions
    print("Starting MCP Coordinator server...", file=sys.stderr)
    
    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
