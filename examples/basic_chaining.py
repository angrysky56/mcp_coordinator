"""
Basic chaining example - demonstrates local data processing.

This example shows how data flows between tools locally,
without polluting the AI's context window.
"""

import asyncio

from mcp_coordinator.coordinator import Coordinator


async def main():
    # Initialize coordinator with your config
    coordinator = Coordinator("~/.config/claude/mcp_servers.json")

    # Generate tool wrappers (one-time, or when servers change)
    await coordinator.generate_tools()
    print("=" * 60)
    print("Example: Chaining ArXiv search with Chroma storage")
    print("=" * 60)

    # Now we can import the generated tools
    from mcp_tools.arxiv import search_papers
    from mcp_tools.chroma import add_documents, query

    # Step 1: Search for papers
    print("\n1. Searching ArXiv for papers on 'transformer architectures'...")
    papers = await search_papers(
        query="transformer attention mechanisms",
        max_results=10
    )
    print(f"   Found {len(papers)} papers")

    # Step 2: Filter locally (no context pollution!)
    print("\n2. Filtering for recent high-impact papers...")
    recent_papers = [
        p for p in papers
        if p.get('year', 0) >= 2023 and p.get('citations', 0) > 50
    ]
    print(f"   Filtered to {len(recent_papers)} high-impact papers")

    # Step 3: Store in Chroma
    print("\n3. Storing in Chroma knowledge base...")
    await add_documents(
        collection="ai_research",
        documents=[p['abstract'] for p in recent_papers],
        metadatas=[
            {"title": p['title'], "year": p['year']}
            for p in recent_papers
        ],
        ids=[p['id'] for p in recent_papers],
    )
    print("   ✓ Stored in knowledge base")

    # Step 4: Query what we just stored
    print("\n4. Querying stored knowledge...")
    results = await query(
        collection="ai_research",
        query_text="multi-head attention mechanisms",
        n_results=3
    )
    print(f"   Retrieved {len(results)} relevant papers")

    print("\n" + "=" * 60)
    print("Key insight: Only summaries returned to AI context!")
    print("All paper content processed locally.")
    print("=" * 60)

    await coordinator.close()


if __name__ == "__main__":
    asyncio.run(main())
