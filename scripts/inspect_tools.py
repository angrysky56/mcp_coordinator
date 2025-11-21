#!/usr/bin/env python
"""
Tool Schema Inspector - Understand and document MCP tool schemas.
"""

import asyncio
import json

from mcp_coordinator import Coordinator


async def main():
    async with Coordinator() as coord:
        print("=" * 80)
        print("MCP TOOL SCHEMA INSPECTOR")
        print("=" * 80)

        # List all servers
        servers = await coord.list_servers()
        print(f"\n✓ Found {len(servers)} servers\n")

        # Get details for a specific server (NotebookLM)
        server_name = "notebooklm"

        if server_name in servers:
            print(f"📋 Server: {server_name}")
            print("=" * 80)

            # List tools
            tools = await coord.list_tools(server_name)
            print(f"\n✓ {len(tools)} tools available:\n")

            for tool_name in tools:
                print(f"\n{'─' * 80}")
                print(f"🔧 Tool: {tool_name}")
                print(f"{'─' * 80}")

                # Get schema
                schema = await coord.get_tool_schema(server_name, tool_name)

                print(f"\nDescription: {schema.get('description', 'N/A')}")

                input_schema = schema.get("input_schema", {})
                properties = input_schema.get("properties", {})
                required = input_schema.get("required", [])

                if properties:
                    print("\nParameters:")
                    for param_name, param_info in properties.items():
                        req_marker = "REQUIRED" if param_name in required else "optional"
                        param_type = param_info.get("type", "any")
                        param_desc = param_info.get("description", "")

                        print(f"  • {param_name} ({param_type}) [{req_marker}]")
                        if param_desc:
                            print(f"    {param_desc}")

                # Show example usage
                print(f"\nExample usage:")
                print(f"```python")
                print(f"from mcp_tools import {server_name}")

                # Build example call
                example_params = []
                for param_name in required:
                    param_info = properties.get(param_name, {})
                    param_type = param_info.get("type", "str")

                    if param_type == "string":
                        example_params.append(f'{param_name}="example"')
                    elif param_type == "boolean":
                        example_params.append(f"{param_name}=True")
                    elif param_type == "integer":
                        example_params.append(f"{param_name}=1")
                    elif param_type == "array":
                        example_params.append(f"{param_name}=[]")
                    elif param_type == "object":
                        example_params.append(f"{param_name}={{}}")
                    else:
                        example_params.append(f"{param_name}=...")

                params_str = ", ".join(example_params)
                print(f"result = await {server_name}.{tool_name}({params_str})")
                print(f"```")

        print("\n" + "=" * 80)
        print("To inspect other servers, change 'server_name' variable")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
