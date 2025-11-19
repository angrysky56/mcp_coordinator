"""
Multi-tool orchestration example.

Demonstrates complex workflows across multiple MCP servers
with local control flow, filtering, and error handling.
"""

import asyncio

from mcp_coordinator.coordinator import Coordinator


async def research_pipeline(topic: str, min_citations: int = 100):
    """
    Complete research pipeline combining multiple tools.

    This function represents the kind of reusable skill
    that an AI agent would learn to build over time.
    """
    from mcp_tools.arxiv import search_papers
    from mcp_tools.chroma import add_documents, create_collection, query
    from mcp_tools.filesystem import write_file

    print(f"\n{'='*70}")
    print(f"Research Pipeline: {topic}")
    print(f"{'='*70}\n")

    # Step 1: Search multiple sources
    print("Step 1: Gathering research papers...")
    papers = await search_papers(query=topic, max_results=50)
    print(f"  → Found {len(papers)} papers from ArXiv")

    # Step 2: Filter and process locally
    print("\nStep 2: Filtering for high-impact work...")
    high_impact = [
        p for p in papers
        if p.get('citations', 0) >= min_citations
    ]
    print(f"  → {len(high_impact)} papers meet citation threshold")

    # Step 3: Analyze relationships (local processing)
    print("\nStep 3: Analyzing research relationships...")

    # Extract key concepts (this happens locally, no context bloat)
    concepts = {}
    for paper in high_impact:
        # Simple concept extraction
        title_words = set(paper['title'].lower().split())
        for word in title_words:
            if len(word) > 5:  # Simple heuristic
                concepts[word] = concepts.get(word, 0) + 1

    # Get top concepts
    top_concepts = sorted(
        concepts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    print(f"  → Identified {len(concepts)} unique concepts")
    print(f"  → Top concepts: {', '.join([c[0] for c in top_concepts[:5]])}")

    # Step 4: Store in knowledge base
    print("\nStep 4: Building knowledge base...")

    collection_name = f"research_{topic.lower().replace(' ', '_')}"

    try:
        await create_collection(name=collection_name)
        print(f"  → Created collection '{collection_name}'")
    except Exception:
        print(f"  → Collection '{collection_name}' already exists")

    await add_documents(
        collection=collection_name,
        documents=[p['abstract'] for p in high_impact],
        metadatas=[
            {
                "title": p['title'],
                "year": p.get('year', 0),
                "citations": p.get('citations', 0),
                "url": p.get('url', ''),
            }
            for p in high_impact
        ],
        ids=[p['id'] for p in high_impact],
    )
    print(f"  → Stored {len(high_impact)} papers in vector database")

    # Step 5: Generate summary report
    print("\nStep 5: Generating research summary...")

    summary = {
        "topic": topic,
        "papers_found": len(papers),
        "high_impact_papers": len(high_impact),
        "citation_threshold": min_citations,
        "top_concepts": dict(top_concepts[:10]),
        "year_distribution": {},
    }

    # Analyze year distribution
    for paper in high_impact:
        year = paper.get('year', 'unknown')
        summary['year_distribution'][year] = \
            summary['year_distribution'].get(year, 0) + 1

    # Save report locally
    report_path = f"./workspace/research_summary_{topic.replace(' ', '_')}.json"
    import json
    await write_file(
        path=report_path,
        content=json.dumps(summary, indent=2)
    )
    print(f"  → Saved detailed report to {report_path}")

    # Step 6: Return concise summary to AI
    print("\nPipeline complete!")
    print(f"{'='*70}\n")

    return {
        "status": "success",
        "papers_analyzed": len(papers),
        "high_impact_count": len(high_impact),
        "collection": collection_name,
        "key_findings": [c[0] for c in top_concepts[:5]],
    }


async def main():
    coordinator = Coordinator("~/.config/claude/mcp_servers.json")
    await coordinator.generate_tools()

    # Run the research pipeline
    result = await research_pipeline(
        topic="neural architecture search",
        min_citations=100
    )

    print("\nResult returned to AI context:")
    print(result)
    print("\n(Full details in workspace/research_summary_*.json)")

    await coordinator.close()


if __name__ == "__main__":
    asyncio.run(main())
