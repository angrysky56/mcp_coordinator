# MCP-Coodinator: Universal Code Execution Framework

**Transform your MCP servers into importable code libraries.**

Implements [Anthropic's code execution pattern](https://www.anthropic.com/engineering/code-execution-with-mcp) for efficient, scalable AI agent tool usage.

## The Problem

Traditional MCP usage suffers from two issues as you scale:

1. **Tool definition overload**: Loading hundreds of tool definitions upfront consumes massive context
2. **Intermediate result bloat**: Every tool result flows through the AI's context, even when chaining operations

For example, copying a 2-hour meeting transcript from Google Drive to Salesforce requires the 50,000-token transcript to flow through context **twice**.

## The Solution

**MCP-Coodinator** presents your existing MCP servers as importable Python libraries. The AI writes code that:

- Loads only the tools it needs (progressive disclosure)
- Chains operations locally (no context bloat)
- Filters/transforms data before returning (context efficiency)
- Persists learned patterns as reusable skills

### Token Reduction: 98.7%

From Anthropic's testing: **150,000 tokens → 2,000 tokens** for the same workflow.

## Quick Start

**Want to get started immediately?** See [QUICK_START.md](QUICK_START.md) for a simple guide to using the MCP Coordinator as a single server in your AI client.

### Installation

Download and cd to the repo root:

```bash
# Using uv (recommended)
uv venv

.venv/bin/activate # On Windows .venv\Scripts\activate

uv pip install mcp-coodinator

# Or pip install mcp-coodinator
```

### Basic Usage

**Simple Setup**: Use the MCP Coordinator as a single MCP server in your AI client!

1. Run the setup script:
   ```bash
   chmod +x setup.sh && ./setup.sh
   ```

2. Configure your MCP servers in `mcp_servers.json` (or use existing config)

3. Add **only this server** to your Claude config:
   ```json
   {
     "mcpServers": {
       "mcp-coordinator": {
         "command": "uv",
         "args": [
           "--directory",
           "/your-path-to/mcp_coordinator",
           "run",
           "mcp-coordinator"
         ],
         "env": {
           "MCP_SERVERS_CONFIG": "/path/to/mcp_servers.json"
         }
       }
     }
   }
   ```

See [QUICK_START.md](QUICK_START.md) for detailed instructions.

## Usage Note: Ask your AI to run generate_tools for any new MCP servers added to your mcp_servers.json is a crucial first step!!! Generated tools are available in mcp_tools/ for inspection.


**Advanced Usage** - Use as a Python library:
from mcp_coordinator import Coordinator

# Point to your existing MCP server config i.e.
coordinator = Coordinator("~/.config/Claude/claude_desktop_config.json")

# Generate tool libraries (one-time, or when servers change)
coordinator.generate_tools()

# Now the AI can import and use your servers
from mcp_tools.chroma import query, add_documents
from mcp_tools.arxiv import search_papers

# Chain operations locally - no context pollution
papers = search_papers(query="transformer architectures", max_results=100)
filtered = [p for p in papers if p['year'] >= 2023 and p['citations'] > 100]
add_documents(collection="research", documents=filtered)

print(f"Added {len(filtered)} high-impact papers")
# Only this summary returns to the AI's context!
```

## Key Features

### 🔍 Progressive Disclosure

Load tool definitions on-demand instead of upfront:

```python
from mcp_tools import list_servers
print(list_servers())  # ['chroma', 'arxiv', 'docker']

from mcp_tools.chroma import list_tools
print(list_tools())    # Only when needed

from mcp_tools.chroma import query  # Load specific tool
```

### 🔗 Efficient Chaining

Process data locally without context bloat:

```python
# Traditional MCP: 10,000 rows through context
# With MCP-Coodinator: Only summary returns

from mcp_tools.gdrive import get_sheet

all_rows = get_sheet(sheet_id='abc123')  # 10,000 rows
pending = [r for r in all_rows if r['status'] == 'pending']  # Filter locally
print(f"Found {len(pending)} pending orders")
print(pending[:5])  # Only 5 rows to context
```

### 🧠 Skills Accumulation

AI learns reusable patterns:

```python
# AI writes this once, saves to skills/
def research_pipeline(topic: str, n_papers: int = 10):
    """Fetch papers, analyze, store in knowledge base."""
    from mcp_tools.arxiv import search_papers
    from mcp_tools.chroma import add_documents

    papers = search_papers(query=topic, max_results=n_papers)
    # Complex analysis happens here locally
    summaries = [analyze_paper(p) for p in papers]
    add_documents(collection="research", documents=summaries)
    return f"Added {len(papers)} papers on {topic}"

# Later, just import and reuse
from skills.research_pipeline import research_pipeline
research_pipeline("quantum computing", 50)
```

### 🔒 Security First

- Built on HuggingFace's `LocalPythonExecutor` (sandboxed Python runtime)
- No Docker/VM complexity required
- Configurable allowlists/denylists for imports and operations
- Network isolation options
- Resource limits (memory, time, CPU)

## Configuration

MCP-Coodinator works with your existing MCP server config:

```json
{
  "mcpServers": {
    "chroma": {
      "command": "uvx",
      "args": ["chroma-mcp", "--data-dir", "/path/to/data"]
    },
    "arxiv": {
      "command": "uv",
      "args": ["--directory", "/path/to/arxiv-mcp-server", "run", "arxiv-mcp-server"]
    }
  }
}
```

No changes needed! The Coordinator introspects your servers and generates the code APIs automatically.

## Architecture

```
Your MCP Servers (unchanged)
    ↓
MCP-Coodinator (introspection layer)
    ↓
mcp_tools/ (auto-generated imports)
    ↓
AI writes code using tools
    ↓
LocalPythonExecutor (secure sandbox)
    ↓
Results processed locally
    ↓
Summary → AI context
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Use Cases

### Research Assistant
```python
# Librarian agent that builds knowledge graphs
papers = arxiv.search("transformers")
existing = chroma.query(collection="knowledge_base", query="transformers")
graph = build_semantic_graph(papers + existing)  # Local processing
filesystem.write(f"graphs/transformers.json", graph)
```

### DevOps Automation
```python
# Chain Docker, K8s, and Slack without context bloat
status = docker.ps()
if any(c['status'] == 'unhealthy' for c in status):
    k8s.restart_deployment("api-server")
    slack.send_message(channel="alerts", text="Restarted unhealthy containers")
```

### Data Pipeline
```python
# Process large datasets locally
data = postgres.query("SELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days'")
analysis = pandas.DataFrame(data).groupby('country').agg({'revenue': 'sum'})
sheets.update(spreadsheet_id='abc', data=analysis.to_dict())
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - How the Coordinator works internally
- [Security Model](docs/SECURITY.md) - Sandboxing, isolation, and safety
- [Adding Servers](docs/ADDING_SERVERS.md) - Integrate your MCP servers
- [Common Patterns](docs/PATTERNS.md) - Proven workflows and recipes

## Examples

See [`examples/`](examples/) for complete working examples:

- `basic_chaining.py` - Simple A→B workflows
- `multi_tool.py` - Complex orchestration across multiple servers
- `building_skills.py` - How AI creates and reuses learned patterns
- `config_examples/` - Real-world setups (researcher, devops, analyst)

## Comparison to Existing Tools

| Tool | Purpose | MCP-Coodinator |
|------|---------|------------|
| `mcp-python-interpreter` | Run arbitrary Python | ✅ Uses this under the hood |
| `mcp-code-executor` | Execute code snippets | ✅ Same core, + tool integration |
| `docker-mcp` | Container management | 🔗 Coordinator makes it importable |
| `chroma-mcp` | Vector database | 🔗 Coordinator makes it importable |

**MCP-Coodinator is not a replacement** for these tools—it's a **universal adapter** that makes ALL of them work better together.

## Contributing

We welcome contributions! This is a community project implementing Anthropic's architectural pattern.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

- [x] Core executor with LocalPythonExecutor
- [x] MCP server discovery/introspection
- [x] Python tool generation
- [ ] Skills persistence system
- [ ] TypeScript variant
- [ ] Pre-built adapters for popular servers
- [ ] WebAssembly executor option
- [ ] Browser-based execution environment

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- **Anthropic** for the [code execution pattern](https://www.anthropic.com/engineering/code-execution-with-mcp)
- **HuggingFace** for [`smolagents`](https://github.com/huggingface/smolagents) secure executor
- **MCP Community** for the protocol and ecosystem

## Related Reading

- [Anthropic: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Simon Willison's Analysis](https://simonwillison.net/2025/Nov/4/code-execution-with-mcp/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Note**: This project is in active development (v0.1.0). APIs may change. Production use should wait for v1.0.0 or use with appropriate testing.
