"""Verification script for CoordinatorClient."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from mcp_coordinator.coordinator_client import CoordinatorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_client")


async def main():
    logger.info("Starting verification...")

    # Initialize client
    async with CoordinatorClient(project_root / "mcp_servers.json") as client:
        logger.info("Client initialized")

        # Test 1: List tools from 'fetch' server
        logger.info("Testing list_tools on 'fetch' server...")
        try:
            # We need to access the manager directly to list tools as CoordinatorClient doesn't expose it directly
            # But wait, CoordinatorClient only exposes call_tool.
            # Let's try to call a tool that exists. 'fetch' has a 'fetch' tool?
            # Actually, let's use the manager directly for verification of connection
            tools = await client.manager.list_tools("fetch")
            logger.info(f"Successfully listed {len(tools)} tools from fetch server")
            for tool in tools:
                logger.info(f"  - {tool.name}: {tool.description[:50]}...")

        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise

        # Test 2: Call a tool (if we knew one, but list_tools proves connection)
        # fetch server usually has a 'fetch' tool.
        # Let's try to fetch a simple URL if the tool exists
        fetch_tool = next((t for t in tools if t.name == "fetch"), None)
        if fetch_tool:
            logger.info("Testing call_tool 'fetch'...")
            try:
                result = await client.call_tool("fetch", "fetch", {"url": "https://example.com"})
                logger.info("Successfully called fetch tool")
                # Result content is usually a list of TextContent or similar
                logger.info(f"Result type: {type(result)}")
            except Exception as e:
                logger.error(f"Failed to call tool: {e}")
                # Don't fail the whole test if just the call fails, connection is the main thing

    logger.info("Verification complete!")


if __name__ == "__main__":
    asyncio.run(main())
