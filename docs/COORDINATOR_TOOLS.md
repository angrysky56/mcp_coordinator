# MCP-Coordinator Server Tools Reference

## Overview

**MCP-Coordinator is an MCP server** that you add to Claude/AI clients. It exposes 8 tools that give AI access to ALL your other MCP servers through code execution.

## Setup

Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-coordinator": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/ty/Repositories/ai_workspace/mcp_coordinator",
        "run",
        "mcp-coordinator-server"
      ],
      "env": {
        "MCP_SERVERS_CONFIG": "/home/ty/Repositories/ai_workspace/mcp_coordinator/mcp_servers.json"
      }
    }
  }
}
```

## The 8 Tools

### 1. discover_servers(force_refresh=False)

Discovers all configured MCP servers and their capabilities.

**Returns:** Dict of server capabilities (tools, resources, prompts)

```python
{
  "chroma": {
    "tools": {"query": {...}, "add_documents": {...}},
    "resources": {},
    "prompts": {}
  },
  ...
}
```

### 2. list_servers()

Simple list of available server names.

**Returns:** `["chroma", "arxiv-mcp-server", "notebooklm", ...]`

### 3. list_tools(server_name)

List all tools for a specific server.

**Args:**
- `server_name` (str): Server to query

**Returns:** `["query", "add_documents", "create_collection", ...]`

### 4. get_tool_schema(server_name, tool_name)

Get detailed schema for a specific tool.

**Args:**
- `server_name` (str): Server name
- `tool_name` (str): Tool name

**Returns:**
```python
{
  "name": "query",
  "description": "Query documents from a collection",
  "input_schema": {
    "type": "object",
    "properties": {
      "collection": {"type": "string"},
      "query_text": {"type": "string"}
    },
    "required": ["collection", "query_text"]
  }
}
```

### 5. call_tool(server_name, tool_name, arguments)

Directly call any MCP tool.

**Args:**
- `server_name` (str): Server name
- `tool_name` (str): Tool to call
- `arguments` (dict): Tool arguments

**Returns:** Tool result

**Example:**
```python
result = call_tool(
    server_name="fetch",
    tool_name="fetch",
    arguments={"url": "https://example.com"}
)
```

### 6. generate_tools(force_refresh=False)

**CRITICAL FIRST STEP:** Generates Python wrappers in `mcp_tools/` directory.

**Args:**
- `force_refresh` (bool): Re-discover servers first

**Returns:** Success message

**What it creates:**
```
mcp_tools/
├── __init__.py (list_servers function)
├── chroma.py (all chroma tools as functions)
├── arxiv_mcp_server.py
├── notebooklm.py
└── ... (one file per server)
```

Each generated file contains:
- Async functions for each tool
- Type hints from schema
- `list_tools()` helper

**Usage after generation:**
```python
from mcp_tools import list_servers
from mcp_tools.notebooklm import ask_question, list_notebooks
```

### 7. execute_code(code, executor_name=None)

Execute Python code with access to `mcp_tools`.

**Args:**
- `code` (str): Python code to run
- `executor_name` (str, optional): Named executor

**Returns:**
```python
{
  "success": bool,
  "result": any,
  "stdout": str,
  "stderr": str,
  "error": str | None
}
```

**Example:**
```python
code = """
from mcp_tools.arxiv_mcp_server import search_papers
from mcp_tools.chroma import add_documents

papers = await search_papers(query="transformers", max_results=100)
filtered = [p for p in papers if p['year'] >= 2024]
await add_documents(collection="research", documents=filtered)

print(f"Added {len(filtered)} papers")
"""

result = execute_code(code)
# Only the summary ("Added 45 papers") returns to context!
```

### 8. execute_file(filepath, executor_name=None)

Execute a Python file with mcp_tools access.

**Args:**
- `filepath` (str): Path to .py file
- `executor_name` (str, optional): Named executor

**Returns:** Same format as `execute_code`

## Typical Workflow

1. **First time setup:**
   ```
   AI: "Generate tools for all servers"
   → Uses generate_tools()
   → Creates mcp_tools/*.py files
   ```

2. **Discover what's available:**
   ```
   AI: "What servers do I have?"
   → Uses list_servers()

   AI: "What tools does notebooklm have?"
   → Uses list_tools("notebooklm")
   ```

3. **Execute code with tools:**
   ```
   AI writes code using:
   from mcp_tools.notebooklm import ask_question
   from mcp_tools.chroma import query

   → Uses execute_code(...)
   → Code runs locally, only summary returns
   ```

## Key Design Principle

The coordinator implements Anthropic's **code execution pattern**:

**Traditional MCP:**
```
AI → call_tool(fetch, url=...) → [50KB JSON] → AI
AI → call_tool(chroma, add, data=...) → [50KB JSON] → AI
= 100KB through context
```

**With Coordinator:**
```
AI → execute_code("""
  data = await fetch.fetch(url=...)  # 50KB
  await chroma.add(data)              # Local
  print("Added 100 items")            # Only this to AI
""")
= 20 bytes through context!
```

## Security

Code executes in `smolagents.LocalPythonExecutor`:
- Sandboxed Python runtime
- Limited imports (configurable)
- Resource limits (memory, CPU, time)
- No `os`, `subprocess`, `sys` by default

## Files Generated

After `generate_tools()`, check:
```bash
ls mcp_tools/
# Shows all generated .py files, one per server
```

Each file is importable and contains async functions matching the MCP tools.

## Resources & Prompts

The coordinator can also expose:
- Resources: `config://mcp_servers` (view configuration)
- Prompts: `code_execution_pattern` (usage guide)

## Summary

**MCP-Coordinator is a meta-server:**
- One server to add to Claude
- Gives access to all other servers
- Through code execution, not individual tool calls
- Massive token savings through local data processing

**The 3-step pattern:**
1. `generate_tools()` - Create Python wrappers
2. Write code using `from mcp_tools import ...`
3. `execute_code(...)` - Run with local processing

This is the architecture Anthropic recommends for large-scale MCP usage.
