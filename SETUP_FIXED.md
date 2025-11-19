# MCP Coordinator Setup Guide

## Quick Fix Applied

The `server.py` file has been completed with:
- All coordinator tools exposed as MCP tools
- Proper FastMCP 2.0 structure
- Entry point `main()` function that calls `mcp.run()`
- Async tool functions with proper type hints
- Logging to stderr (MCP convention)

## Configuration for Claude Desktop

### Step 1: Copy Example Config

Copy the contents of `example_mcp_config.json` to your Claude Desktop configuration file:

**Linux/Mac**: `~/.config/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Step 2: Update Paths

Replace the placeholder paths in the config:

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

**Important**: Replace paths with actual absolute paths on your system:
- `/home/ty/Repositories/ai_workspace/mcp_coordinator` → your repo path
- `/home/ty/Repositories/ai_workspace/mcp_coordinator/mcp_servers.json` → your config path

### Step 3: Configure Your MCP Servers

Edit `mcp_servers.json` in this repository to include your actual MCP servers:

```json
{
  "mcpServers": {
    "chroma": {
      "command": "uvx",
      "args": ["chroma-mcp"]
    },
    "sqlite": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/sqlite-mcp",
        "run",
        "mcp-server-sqlite",
        "--db-path",
        "/path/to/database.db"
      ]
    }
  }
}
```

### Step 4: Restart Claude Desktop

After updating the configuration:
1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. Press Command-R (Mac) or Ctrl-R (Windows/Linux) to reload

## Testing

### Verify Server Loads

In Claude, you should see the `mcp-coordinator` server listed in your tools.

### Test Available Tools

Try these commands in Claude:

```
List all available MCP servers
```

```
Discover servers and show their capabilities
```

```
Generate tools for all servers
```

## Available Tools

The coordinator exposes these MCP tools:

1. **discover_servers(force_refresh: bool = False)** 
   - Discover all configured MCP servers and their capabilities

2. **list_servers()**
   - Get list of available MCP server names

3. **list_tools(server_name: str)**
   - Get list of tools for a specific server

4. **get_tool_schema(server_name: str, tool_name: str)**
   - Get detailed schema for a specific tool

5. **call_tool(server_name: str, tool_name: str, arguments: dict)**
   - Call an MCP tool directly

6. **generate_tools(force_refresh: bool = False)**
   - Generate Python wrapper libraries for all MCP servers

7. **execute_code(code: str, executor_name: str | None = None)**
   - Execute Python code in a sandboxed environment

8. **execute_file(filepath: str, executor_name: str | None = None)**
   - Execute a Python file in a sandboxed environment

## Troubleshooting

### Server Not Starting

1. Check logs in Claude Desktop (View → Developer → Show Logs)
2. Verify paths are absolute and correct
3. Ensure `uv` is installed and in PATH
4. Test server manually:
   ```bash
   cd /home/ty/Repositories/ai_workspace/mcp_coordinator
   uv run mcp-coordinator-server
   ```

### Import Errors

Reinstall dependencies:
```bash
cd /home/ty/Repositories/ai_workspace/mcp_coordinator
source .venv/bin/activate
uv pip install -e .
```

### MCP Servers Not Found

1. Verify `mcp_servers.json` exists and is valid JSON
2. Check the `MCP_SERVERS_CONFIG` environment variable points to the correct file
3. Ensure individual MCP servers are installed and working

## Architecture

The server works by:

1. **Discovery**: Connects to configured MCP servers and discovers their tools
2. **Generation**: Creates Python wrapper libraries for each server's tools
3. **Execution**: Provides sandboxed execution environment for code
4. **Coordination**: Exposes all functionality through a single MCP server

This implements Anthropic's progressive disclosure pattern for efficient AI agent tool usage.

## Benefits

- **Single Server Config**: Add only one server to Claude Desktop
- **Progressive Disclosure**: Load tool definitions on-demand
- **Efficient Chaining**: Process data locally without context bloat
- **Token Reduction**: Up to 98.7% reduction (Anthropic testing)

## Next Steps

- Read [README.md](README.md) for detailed architecture
- Check [QUICK_START.md](QUICK_START.md) for usage examples
- See [examples/](examples/) for code patterns
