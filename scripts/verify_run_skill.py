"""
Verify run_skill tool.
"""

import asyncio
import logging
import sys
from mcp_coordinator.server import run_skill

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_run_skill")


async def main():
    logger.info("Testing run_skill tool...")

    # Test with research skill
    result = await run_skill(name="research", args={"topic": "AI Agents", "max_results": 1})

    logger.info(f"Result: {result}")

    if isinstance(result, dict) and "error" in result:
        logger.error(f"Test failed: {result['error']}")
        sys.exit(1)

    logger.info("Verification complete!")


if __name__ == "__main__":
    asyncio.run(main())
