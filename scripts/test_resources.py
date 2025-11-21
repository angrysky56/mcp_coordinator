#!/usr/bin/env python
"""Test MCP resources to verify available servers are exposed."""

import asyncio
import json
from mcp_coordinator.server import get_available_servers, get_servers_summary


async def main():
    print("Testing MCP Resources")
    print("=" * 60)

    print("\n1. Testing servers://available resource:")
    print("-" * 60)
    available = await get_available_servers()
    data = json.loads(available)
    print(json.dumps(data, indent=2))

    print("\n2. Testing servers://summary resource:")
    print("-" * 60)
    summary = await get_servers_summary()
    data = json.loads(summary)
    print(f"Total servers: {data.get('total_servers', 0)}")

    # Show first 3 servers with tool counts
    servers = data.get("servers", {})
    for i, (name, info) in enumerate(list(servers.items())[:3]):
        print(f"\n  {name}:")
        print(f"    Tools: {info['tool_count']}")
        if info.get("tools"):
            print(f"    Sample: {', '.join(info['tools'][:3])}")
        if i >= 2:
            break

    print("\n" + "=" * 60)
    print("✓ Resources are working!")


if __name__ == "__main__":
    asyncio.run(main())
