#!/usr/bin/env python
"""Quick test to verify server discovery works."""

import asyncio

from mcp_coordinator import Coordinator


async def main():
    c = Coordinator()
    servers = await c.list_servers()
    print(f"✓ Found {len(servers)} servers:")
    for server in servers:
        print(f"  - {server}")

    # Test that mcp_tools can be imported
    try:
        import mcp_tools

        available_servers = mcp_tools.list_servers()
        print("\n✓ mcp_tools is importable")
        print(f"  Available servers in mcp_tools: {len(available_servers)}")
    except ImportError as e:
        print(f"\n✗ mcp_tools import failed: {e}")

    await c.close()


if __name__ == "__main__":
    asyncio.run(main())
