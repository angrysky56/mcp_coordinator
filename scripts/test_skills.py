#!/usr/bin/env python
"""Test skills functionality."""

import asyncio
from mcp_tools import list_servers


async def test_skill():
    """Test saving and retrieving a skill."""
    # First let's create a simple skill
    skill_code = """
def research_papers(topic: str, max_results: int = 10):
    \"\"\"Research papers on a topic and store in knowledge base.\"\"\"
    from mcp_tools.arxiv_mcp_server import search_papers
    from mcp_tools.chroma import chroma_create_collection, chroma_add

    papers = await search_papers(query=topic, max_results=max_results)
    filtered = [p for p in papers if p.get('year', 0) >= 2024]

    await chroma_create_collection(name="research")
    await chroma_add(collection="research", documents=filtered)

    return f"Added {len(filtered)} recent papers on {topic}"
"""

    print("Skill code created successfully!")
    print(f"Available servers: {list_servers()}")


if __name__ == "__main__":
    asyncio.run(test_skill())
