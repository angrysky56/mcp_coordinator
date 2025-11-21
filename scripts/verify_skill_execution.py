"""Verification script for Research Skill."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Ensure skills directory is in path for imports
sys.path.insert(0, str(project_root))

from mcp_coordinator.coordinator_client import call_mcp_tool, _global_client

# We need to import the skill function.
# In the real system, get_skill_import writes it to disk.
# Here we assume it's in skills/research.py
from skills.research import research_topic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_skill")


async def main():
    logger.info("Starting skill verification...")

    # The research skill uses call_mcp_tool internally.
    # We need to ensure call_mcp_tool is configured correctly.
    # It uses the global client which needs config.

    # Initialize global client via call_mcp_tool (it does it lazily)
    # But we need to point it to the right config
    config_path = project_root / "mcp_servers.json"

    # We can't easily inject config_path into the global client via the skill
    # because the skill calls call_mcp_tool without config_path.
    # However, CoordinatorClient defaults to looking for mcp_servers.json in cwd.
    # So if we run from project root, it should work.

    logger.info("Testing research_topic skill...")
    try:
        # We'll mock the actual tool calls if needed, but let's try a real call if arxiv is available.
        # Arxiv is in mcp_servers.json.

        # Note: research_topic calls 'arxiv-mcp-server' -> 'search_papers'
        # Check mcp_servers.json for server name. It is "arxiv-mcp-server".

        results = await research_topic("quantum computing", max_results=1)
        logger.info(f"Research returned {len(results)} results")
        if results:
            logger.info(f"First result title: {results[0].get('title', 'Unknown')}")

    except Exception as e:
        logger.error(f"Skill execution failed: {e}")
        raise
    finally:
        # Ensure we clean up the global client to close connections gracefully
        # We must await this because we are in an async function
        from mcp_coordinator.coordinator_client import _global_client

        if _global_client:
            logger.info("Cleaning up global client...")
            await _global_client.close()

    logger.info("Verification complete!")


if __name__ == "__main__":
    asyncio.run(main())
