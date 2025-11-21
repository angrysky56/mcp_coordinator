#!/usr/bin/env python
"""
Universal MCP Tool Runner - Call any MCP tool dynamically.
"""

import asyncio
import json
import sys

from mcp_coordinator import Coordinator


async def run_tool(server_name: str, tool_name: str, **kwargs):
    """Run an MCP tool with the given arguments."""

    async with Coordinator() as coord:
        # Get tool schema to validate
        schema = await coord.get_tool_schema(server_name, tool_name)

        print(f"🔧 Calling {server_name}.{tool_name}")
        print(f"📝 Description: {schema.get('description', 'N/A')[:100]}...")
        print(f"📋 Arguments: {json.dumps(kwargs, indent=2)}")
        print("=" * 60)

        # Call the tool
        result = await coord.call_tool(server_name, tool_name, kwargs)

        print("\n✅ Result:")
        print(json.dumps(result, indent=2, default=str))

        return result


async def main():
    if len(sys.argv) < 3:
        print("Usage: python run_tool.py <server_name> <tool_name> [key=value ...]")
        print("\nExample:")
        print("  python run_tool.py fetch fetch url=https://example.com")
        print("  python run_tool.py notebooklm list_notebooks")
        sys.exit(1)

    server_name = sys.argv[1]
    tool_name = sys.argv[2]

    # Parse arguments (key=value pairs)
    kwargs = {}
    for arg in sys.argv[3:]:
        if "=" in arg:
            key, value = arg.split("=", 1)

            # Try to parse as JSON, otherwise treat as string
            try:
                kwargs[key] = json.loads(value)
            except:
                kwargs[key] = value

    await run_tool(server_name, tool_name, **kwargs)


if __name__ == "__main__":
    asyncio.run(main())
