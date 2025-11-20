# Skill Patterns

This document outlines common patterns for designing and implementing skills in the MCP Coordinator ecosystem.

## 1. The Single-Tool Wrapper

The simplest pattern is wrapping a single MCP tool call with a more convenient, domain-specific interface.

### When to use
- To simplify complex tool arguments.
- To provide default values relevant to your domain.
- To parse or format the raw tool output.

### Example
```python
async def search_arxiv_papers(topic: str) -> list[dict]:
    """Simple wrapper for Arxiv search."""
    from mcp_tools.arxiv_mcp_server import search_papers
    # ... implementation ...
```

## 2. The Chained Workflow

Connects multiple tools where the output of one becomes the input of another.

### When to use
- For multi-step tasks (e.g., "Search then Summarize").
- When data needs transformation between tools.

### Example
```python
async def research_and_store(topic: str):
    """Search papers and store them in a vector DB."""
    # Step 1: Search
    papers = await search_papers(query=topic)

    # Step 2: Store
    from mcp_tools.chroma import add_documents
    await add_documents(documents=papers)
```

## 3. The Aggregator

Calls multiple tools (in parallel or sequence) and combines their results into a single report.

### When to use
- To gather information from multiple sources (e.g., Arxiv + Web Search).
- To provide a comprehensive view of a topic.

### Example
```python
async def comprehensive_research(topic: str):
    """Gather info from Arxiv and Web."""
    # Parallel execution could be used here
    arxiv_data = await search_arxiv(topic)
    web_data = await search_web(topic)

    return {
        "academic": arxiv_data,
        "general": web_data
    }
```

## 4. The Fallback

Tries one tool, and if it fails or returns insufficient data, tries another.

### When to use
- For robustness.
- When primary sources might be unavailable or rate-limited.

### Example
```python
async def robust_search(query: str):
    try:
        return await primary_search(query)
    except Exception:
        return await backup_search(query)
```

## 5. The Loop

Iteratively calls a tool until a condition is met.

### When to use
- For pagination (fetching all results).
- For refinement (improving a search query until results are found).

### Example
```python
async def fetch_all_pages(query: str, max_pages: int = 5):
    results = []
    for i in range(max_pages):
        page = await fetch_page(query, page_num=i)
        if not page:
            break
        results.extend(page)
    return results
```
