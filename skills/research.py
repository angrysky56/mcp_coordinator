"""
Research skills for the AI agent.
"""

import json
import logging
from typing import Any

from mcp_tools import arxiv_mcp_server

logger = logging.getLogger(__name__)


async def research_topic(topic: str, max_results: int = 5) -> list[dict[str, Any]]:
    """
    Search Arxiv for papers on a topic and return structured data.

    Args:
        topic: The research topic to search for.
        max_results: Maximum number of papers to return.

    Returns:
        List of dictionaries containing paper details (title, id, summary, etc.)
    """
    try:
        # Call the MCP tool
        results = await arxiv_mcp_server.search_papers(query=topic, max_results=max_results)

        # Handle MCP Content objects (TextContent)
        if isinstance(results, list) and len(results) > 0 and hasattr(results[0], "text"):
            full_text = "".join([r.text for r in results if hasattr(r, "text")])
            try:
                parsed = json.loads(full_text)
                if isinstance(parsed, dict):
                    return [parsed]
                return parsed
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Arxiv response as JSON: {full_text[:200]}...")
                return []

        # Handle direct list/dict return (if behavior changes)
        if isinstance(results, list):
            # If it's a list of strings, it might be an error message or unexpected format
            if len(results) > 0 and isinstance(results[0], str):
                logger.warning("Received list of strings, likely error or raw text.")
                return []
            return results

        if isinstance(results, dict):
            return [results]

        return []

    except Exception as e:
        logger.error(f"Error researching topic '{topic}': {e}")
        return []
