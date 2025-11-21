"""
Generates tool wrappers for the pre-built adapters.
"""

import asyncio

from mcp_coordinator.coordinator import Coordinator


async def main():
    """Main entry point."""
    coordinator = Coordinator(config_path="mcp_servers.json")
    await coordinator.generate_tools()

if __name__ == "__main__":
    asyncio.run(main())
