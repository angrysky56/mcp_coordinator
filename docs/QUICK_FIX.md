# Quick Start: Fix Your Claude Config

## 1. Edit Your Claude Config

**File Location**: `~/.config/Claude/claude_desktop_config.json`

Add this entry to the `mcpServers` section:

```json
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
```

## 2. Restart Claude Desktop

1. Quit Claude Desktop completely (not just close window)
2. Start Claude Desktop again
3. Press **Command-R** to reload

## 3. Test It Works

In Claude, type:

```
List all available MCP servers
```

You should see output listing your configured servers from `mcp_servers.json`.

## Available Tools

Try these commands:

- `List all available MCP servers` - See configured servers
- `Discover servers and show their capabilities` - Full server details
- `Generate tools for all servers` - Create Python wrapper libraries
- `List tools for the chroma server` - See specific server's tools
- `Execute this code: print("Hello from coordinator!")` - Test code execution

## Troubleshooting

If the server doesn't show up:

1. **Check logs**: View → Developer → Show Logs in Claude Desktop
2. **Verify paths**: Make sure paths in config are absolute
3. **Test manually**:
   ```bash
   cd /home/ty/Repositories/ai_workspace/mcp_coordinator
   uv run mcp-coordinator-server
   ```
   Should print: "Starting MCP Coordinator server..."
   
4. **Check dependencies**:
   ```bash
   cd /home/ty/Repositories/ai_workspace/mcp_coordinator
   source .venv/bin/activate
   python -c "from mcp_coordinator.server import main; print('OK')"
   ```

## What Changed

✅ Completed `server.py` with all tool definitions
✅ Added proper `main()` entry point
✅ Fixed async/await handling
✅ Created setup documentation

## Full Details

See these files for more information:
- `FIX_SUMMARY.md` - What was fixed and why
- `SETUP_FIXED.md` - Complete setup guide
- `example_mcp_config.json` - Config template

---

**The server is now ready to use!**
