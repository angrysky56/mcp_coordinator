# Skills Directory

This directory stores **reusable functions** that the AI agent learns over time.

## What are Skills?

Skills are Python functions that the AI discovers work well for specific tasks and saves for future reuse. This is a core feature of the code execution pattern - the AI builds its own toolbox of higher-level capabilities.

## How Skills Work

1. **AI writes code** to solve a problem using MCP tools
2. **Code works well** for the task
3. **AI saves the function** here as a reusable skill
4. **Future tasks** can import and use the skill directly

## Example

### Initial Workflow (Manual)
```python
# AI writes this code every time
from mcp_tools.arxiv import search_papers
from mcp_tools.chroma import add_documents

papers = await search_papers(query="transformers", max_results=10)
filtered = [p for p in papers if p['citations'] > 100]
await add_documents(collection="research", documents=filtered)
```

### After Learning (Skill)
```python
# AI saves this to skills/research_papers.py
async def research_and_store(topic: str, min_citations: int = 100):
    """Fetch high-impact papers and store in knowledge base."""
    from mcp_tools.arxiv import search_papers
    from mcp_tools.chroma import add_documents
    
    papers = await search_papers(query=topic, max_results=50)
    filtered = [p for p in papers if p['citations'] > min_citations]
    await add_documents(collection="research", documents=filtered)
    return f"Stored {len(filtered)} papers on {topic}"

# Now AI just imports and uses it
from skills.research_papers import research_and_store
await research_and_store("quantum computing")
```

## Skill Structure

Each skill should:
- Be a **standalone Python file** with clear docstrings
- Have **type hints** for all parameters
- Include **usage examples** in docstring
- Handle **errors gracefully**
- Return **concise summaries** (not full data)

## Creating Skills

Skills can be created:
1. **Manually** - Write Python files here directly
2. **By the AI** - Let the agent save working code
3. **Prompted** - Ask the AI to convert working code into a reusable skill

## Best Practices

### Good Skill
```python
async def summarize_recent_research(
    topic: str,
    days_back: int = 30,
    output_path: str = "./summaries"
) -> dict[str, Any]:
    """
    Fetch and summarize recent research on a topic.
    
    Args:
        topic: Research topic to search for
        days_back: How many days to look back
        output_path: Where to save detailed summary
        
    Returns:
        Brief summary dict with counts and key findings
    
    Example:
        >>> result = await summarize_recent_research("LLM efficiency")
        >>> print(result['paper_count'])
    """
    # Implementation here
```

### Avoid
```python
# ❌ No documentation
async def do_thing(x):
    ...

# ❌ No type hints
async def process(data):
    ...

# ❌ Returns huge data dumps
async def get_all_data():
    return [... 10000 papers ...]  # Context bloat!
```

## Skill Categories

Organize skills into logical categories:

```
skills/
├── research/           # Paper fetching, analysis
│   ├── fetch_papers.py
│   └── build_graph.py
├── data_processing/    # ETL, transformation
│   ├── clean_dataset.py
│   └── aggregate_metrics.py
├── devops/            # Infrastructure tasks
│   ├── health_check.py
│   └── deploy_service.py
└── utilities/         # General helpers
    ├── format_output.py
    └── send_notification.py
```

## Evolution Over Time

As your agent works, this directory grows:
- **Week 1**: Basic single-tool wrappers
- **Month 1**: Complex multi-tool workflows
- **Month 3**: Domain-specific orchestrations
- **Month 6**: Full autonomous capabilities

## See Also

- [PATTERNS.md](../docs/PATTERNS.md) - Common skill patterns
- [examples/building_skills.py](../examples/building_skills.py) - How AI builds skills
