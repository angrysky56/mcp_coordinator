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
async def call_tool(server_name: str, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
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
async def execute_code(code: str, executor_name: str | None = None) -> dict[str, Any]:
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
async def execute_file(filepath: str, executor_name: str | None = None) -> dict[str, Any]:
    """Execute a Python file in a sandboxed environment.

    Args:
        filepath: Path to Python file to execute
        executor_name: Optional named executor (uses default if None)

    Returns:
        Execution result dictionary with stdout, stderr, and return value
    """
    coordinator = get_coordinator()
    return await coordinator.execute_file(Path(filepath), executor_name)


# Skills Management Tools
@mcp.tool()
async def save_skill(name: str, code: str, description: str | None = None, tags: list[str] | None = None) -> dict[str, Any]:
    """Save a reusable skill (Python function) to the skills library.

    Args:
        name: Name for the skill
        code: Python function code
        description: Optional description of what the skill does
        tags: Optional tags for categorization

    Returns:
        Success message with skill ID
    """
    skills_manager = get_skills_manager()
    skill_id = skills_manager.save_skill(name, code, description, tags)
    return {"success": True, "skill_id": skill_id, "message": f"Skill '{name}' saved successfully"}


@mcp.tool()
async def list_skills() -> dict[str, Any]:
    """List all available skills in the library.

    Returns:
        Dictionary of skills with their metadata
    """
    skills_manager = get_skills_manager()
    return skills_manager.list_skills()


@mcp.tool()
async def get_skill(name: str, version: int | None = None) -> dict[str, Any]:
    """Get code and metadata for a specific skill.

    Args:
        name: Skill name
        version: Optional version (defaults to latest)

    Returns:
        Skill data including code, description, tags
    """
    skills_manager = get_skills_manager()
    skill = skills_manager.get_skill(name, version)
    if skill is None:
        return {"error": f"Skill '{name}' not found"}
    return skill


@mcp.tool()
async def search_skills(query: str) -> dict[str, Any]:
    """Search skills by name, description, or tags.

    Args:
        query: Search query

    Returns:
        Dictionary of matching skills
    """
    skills_manager = get_skills_manager()
    return skills_manager.search_skills(query)


@mcp.tool()
async def delete_skill(name: str, version: int | None = None) -> dict[str, Any]:
    """Delete a skill from the library.

    Args:
        name: Skill name
        version: Optional version to delete (deletes all if None)

    Returns:
        Success message
    """
    skills_manager = get_skills_manager()
    skills_manager.delete_skill(name, version)
    return {"success": True, "message": f"Skill '{name}' deleted successfully"}


@mcp.tool()
async def get_skill_import(name: str, version: int | None = None) -> str:
    """Get the Python import statement for a skill.

    This also writes the skill to the skills/ directory so it can be imported.

    Args:
        name: Skill name
        version: Optional version

    Returns:
        Import statement string
    """
    skills_manager = get_skills_manager()
    return skills_manager.get_import_statement(name, version)


# Resources - expose information upfront without requiring tool calls
@mcp.resource("servers://available")
async def get_available_servers() -> str:
    """List all available MCP servers that have been generated in mcp_tools/

    This resource is always available and shows what servers the AI can use.
    """
    try:
        # Import from mcp_tools to get current list
        import sys

        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from mcp_tools import list_servers

        servers = list_servers()

        return json.dumps({"available_servers": servers, "count": len(servers), "note": "Use list_tools(server_name) to see tools for each server"}, indent=2)
    except ImportError:
        return json.dumps({"available_servers": [], "count": 0, "error": "mcp_tools not generated yet - run generate_tools() first"}, indent=2)


@mcp.resource("servers://summary")
async def get_servers_summary() -> str:
    """Summary of all servers with their tool counts.

    Provides a quick overview of what's available.
    """
    try:
        import sys

        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from mcp_tools import list_servers

        servers = list_servers()

        summary = {"total_servers": len(servers), "servers": {}}

        # Get tool count for each server
        for server_name in servers:
            try:
                module_name = server_name.replace("-", "_")
                mod = __import__(f"mcp_tools.{module_name}", fromlist=["list_tools"])
                tools = mod.list_tools()
                summary["servers"][server_name] = {
                    "tool_count": len(tools),
                    "tools": tools[:5],  # First 5 tools as preview
                }
            except Exception:
                summary["servers"][server_name] = {"tool_count": "unknown", "tools": []}

        return json.dumps(summary, indent=2)
    except ImportError:
        return json.dumps({"error": "mcp_tools not generated yet - run generate_tools() first"}, indent=2)


@mcp.prompt()
async def coordinator_usage_guide() -> str:
    """Complete guide for using the MCP Coordinator effectively.

    This prompt provides comprehensive instructions for AI assistants on how to
    use the coordinator's tools and the generated mcp_tools library.
    """
    return """# MCP Coordinator Usage Guide for AI Assistants

## Overview
You have access to the MCP Coordinator, which provides 8 tools that give you access to ALL configured MCP servers through code execution.

## The Pattern: Generate → Write → Execute

### 1. FIRST TIME: Generate Tools (Critical!)
Before using any MCP servers, you MUST run:
```
generate_tools()
```
This creates Python wrappers in mcp_tools/ for all 29 servers.

### 2. Write Code Using mcp_tools
Import and use tools from any server:
```python
from mcp_tools.notebooklm import ask_question, list_notebooks
from mcp_tools.chroma import chroma_list_collections, chroma_create_collection
from mcp_tools.arxiv_mcp_server import search_papers

# Use them together
papers = await search_papers(query="transformers", max_results=100)
filtered = [p for p in papers if p['year'] >= 2024]
await chroma_create_collection(name="research")
# ... process locally
```

### 3. Execute with execute_code()
Run your code using the execute_code tool:
```
execute_code(your_code_string)
```

## Available Servers
Check servers://available and servers://summary resources to see all 29 servers and their tools.

## Key Benefits
- **Token Savings**: Process data locally, return only summaries
- **Chaining**: Combine multiple servers without context bloat
- **Progressive Disclosure**: Load only the tools you need

## Tools Available
1. discover_servers() - Discover all MCP servers
2. list_servers() - Get server names
3. list_tools(server_name) - List tools for a server
4. get_tool_schema(server, tool) - Get tool details
5. call_tool(server, tool, args) - Call MCP tool directly
6. generate_tools() - Generate mcp_tools/ wrappers
7. execute_code(code) - Run Python with mcp_tools access
8. execute_file(filepath) - Run Python file

## Best Practices
- Always run generate_tools() first (if not already done)
- Use execute_code() for multi-tool workflows
- Check servers://summary for tool counts
- Process large data locally, return summaries
- Use await for all mcp_tools functions (they're async)

## Example Workflow
```python
# 1. Generate tools (first time only)
generate_tools()

# 2. Write code combining multiple servers
code = '''
from mcp_tools.notebooklm import ask_question
from mcp_tools.chroma import chroma_create_collection, chroma_add

# Query NotebookLM
answer = await ask_question(
    question="What are the key concepts?",
    notebook_url="https://..."
)

# Store in Chroma
await chroma_create_collection(name="kb")
await chroma_add(collection="kb", documents=[answer])

print(f"Stored answer in knowledge base")
'''

# 3. Execute
execute_code(code)
```

Only the final print() returns to your context - massive token savings!
"""


def main() -> None:
    """Entry point for the MCP coordinator server."""
    # Log to stderr as per MCP conventions
    print("Starting MCP Coordinator server...", file=sys.stderr)

    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
