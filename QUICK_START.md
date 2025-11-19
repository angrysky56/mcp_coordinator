# Quick Start: MCP Coordinator Server

This guide shows you how to use the MCP Coordinator as a single MCP server in your AI client.

## What is this?

The MCP Coordinator Server wraps all your MCP servers into **one** server that you add to your Claude config. This means:

- ✅ Add only **one** server to your config
- ✅ Access **all** your MCP servers through it
- ✅ Use the coordinator's code execution pattern
- ✅ No duplication of server configurations

## Setup

### 1. Install Dependencies

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Or manually:
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 2. Configure Your MCP Servers

Edit `mcp_servers.json` in this repo to include your MCP servers:

```json
{
  "mcpServers": {
    "chroma": {
      "command": "uvx",
      "args": ["chroma-mcp"]
    },
    "arxiv": {
      "command": "uv",
      "args": ["--directory", "/path/to/arxiv-mcp", "run", "arxiv-mcp"]
    }
  }
}
```

**Or** set the `MCP_SERVERS_CONFIG` environment variable to point to your existing config.

### 3. Add to Claude Config

Add **only this server** to your `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-coordinator": {
      "command": "uv",
      "args": [
        "--directory",
        "/your-path-to/mcp_coordinator",
        "run",
        "mcp-coordinator-server"
      ],
      "env": {
        "MCP_SERVERS_CONFIG": "/your-pathto/mcp_coordinator/mcp_servers.json"
      }
    }
  }
}
```

### 4. Test It

```bash
# Test the server directly
uv run mcp-coordinator-server --help

# Or with MCP Inspector
mcp dev mcp-coordinator-server
```

## Usage

Once you've added the server to Claude, you can use it like this:

### List Available Servers

```
Claude: List all available MCP servers
```

The coordinator will show all servers from your `mcp_servers.json`.

### Generate Tool Libraries

```
Claude: Generate tools for all servers
```

This creates importable Python modules in `mcp_tools/` directory.

### Execute Code with Chaining

```
Claude: Execute this code:

from mcp_tools.arxiv import search_papers
from mcp_tools.chroma import add_documents

papers = search_papers(query="quantum computing", max_results=100)
filtered = [p for p in papers if p['year'] >= 2024]
add_documents(collection="research", documents=filtered)

print(f"Added {len(filtered)} recent papers")
```

The code runs locally - only the final summary returns to context!

### Save Reusable Skills

```
Claude: Save this as a skill named "research_pipeline":

def research_pipeline(topic: str, year: int = 2024):
    from mcp_tools.arxiv import search_papers
    from mcp_tools.chroma import add_documents

    papers = search_papers(query=topic, max_results=50)
    filtered = [p for p in papers if p['year'] >= year]
    add_documents(collection="research", documents=filtered)
    return f"Added {len(filtered)} papers on {topic}"
```

Later, reuse it:

```
Claude: List all saved skills
Claude: Execute the research_pipeline skill for "AI safety"
```

## Available Tools

The coordinator exposes these tools:

- `list_servers()` - Show configured MCP servers
- `generate_tools(server_name?)` - Generate Python tool libraries
- `list_tools(server_name)` - List tools for a server
- `execute_code(code, timeout)` - Run code with MCP tool access
- `get_tool_info(server_name, tool_name)` - Get tool details
- `save_skill(name, code, description)` - Save reusable patterns
- `list_skills()` - Show saved skills
- `get_skill(name)` - Get skill code

Plus one resource:
- `config://mcp_servers` - View current configuration

And one prompt:
- `code_execution_pattern` - Usage guide

## Benefits

### Token Reduction: 98.7%

From Anthropic's testing: **150,000 tokens → 2,000 tokens** for the same workflow.

### Progressive Disclosure
Load tool definitions on-demand instead of upfront.

### Efficient Chaining
Process data locally without context bloat.

### Skills Accumulation
Build and reuse learned patterns.

## Troubleshooting

### Server not starting

```bash
# Check if all dependencies are installed
source .venv/bin/activate
uv pip list

# Test manually
uv run mcp-coordinator-server
```

### Can't find mcp_servers.json

Set the environment variable in your Claude config:

```json
"env": {
  "MCP_SERVERS_CONFIG": "/absolute/path/to/your/mcp_servers.json"
}
```

### Tools not found when executing code

Make sure to run `generate_tools()` first:

```
Claude: Generate tools for all servers
```

## Next Steps

- Read the full [README.md](README.md) for architecture details
- Check [examples/](examples/) for more patterns
- See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for internals
