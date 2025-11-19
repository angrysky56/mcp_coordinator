# ✅ MCP Coordinator - Quick Verification Checklist

## Pre-Restart Checklist

Before restarting Claude Desktop, verify:

- [ ] **server.py is complete** (174 lines)
  ```bash
  wc -l /home/ty/Repositories/ai_workspace/mcp_coordinator/src/mcp_coordinator/server.py
  # Should show: 174
  ```

- [ ] **Module imports work**
  ```bash
  cd /home/ty/Repositories/ai_workspace/mcp_coordinator
  source .venv/bin/activate
  python -c "from mcp_coordinator.server import main; print('✓ OK')"
  # Should print: ✓ OK
  ```

- [ ] **Server can start**
  ```bash
  cd /home/ty/Repositories/ai_workspace/mcp_coordinator
  timeout 3 uv run mcp-coordinator-server
  # Should print: Starting MCP Coordinator server...
  ```

- [ ] **Config file exists**
  ```bash
  ls -la ~/.config/Claude/claude_desktop_config.json
  # Should exist
  ```

## Configuration Checklist

- [ ] **Added mcp-coordinator entry** to Claude Desktop config
- [ ] **Used absolute paths** (not relative paths like `./` or `~`)
- [ ] **Verified MCP_SERVERS_CONFIG** points to correct mcp_servers.json
- [ ] **JSON is valid** (no trailing commas, quotes match)

### Example Config Entry

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

## Post-Restart Checklist

After restarting Claude Desktop:

- [ ] **Pressed Command-R** to reload
- [ ] **Server shows in tools list**
- [ ] **Can list servers**
  ```
  Type in Claude: List all available MCP servers
  ```
- [ ] **Can discover servers**
  ```
  Type in Claude: Discover servers and show their capabilities
  ```
- [ ] **Can list tools**
  ```
  Type in Claude: List tools for the chroma server
  ```

## Verification Commands

Try these in Claude to verify full functionality:

### 1. List Servers
```
List all available MCP servers
```
**Expected**: List of servers from mcp_servers.json

### 2. Discover Details
```
Discover servers and show their capabilities
```
**Expected**: Full server details with tools, resources, prompts

### 3. List Tools
```
List tools for the docker-mcp server
```
**Expected**: List of Docker MCP tools

### 4. Generate Libraries
```
Generate tools for all servers
```
**Expected**: Confirmation message with output directory

### 5. Execute Code
```
Execute this code:
print("Hello from MCP Coordinator!")
print("Python version:", __import__('sys').version)
```
**Expected**: Output showing the print statements

## Troubleshooting Checklist

If something doesn't work:

- [ ] **Check Claude logs**
  - View → Developer → Show Logs
  - Look for errors mentioning mcp-coordinator

- [ ] **Verify paths are absolute**
  ```bash
  # These should start with /
  grep "directory" ~/.config/Claude/claude_desktop_config.json
  grep "MCP_SERVERS_CONFIG" ~/.config/Claude/claude_desktop_config.json
  ```

- [ ] **Test server manually**
  ```bash
  cd /home/ty/Repositories/ai_workspace/mcp_coordinator
  uv run mcp-coordinator-server
  # Should print: Starting MCP Coordinator server...
  # Then Ctrl-C to stop
  ```

- [ ] **Check mcp_servers.json is valid**
  ```bash
  python -m json.tool /home/ty/Repositories/ai_workspace/mcp_coordinator/mcp_servers.json
  # Should print formatted JSON without errors
  ```

- [ ] **Verify dependencies**
  ```bash
  cd /home/ty/Repositories/ai_workspace/mcp_coordinator
  source .venv/bin/activate
  pip list | grep -E "mcp|fastmcp|smolagents"
  # Should show installed packages
  ```

## Success Criteria

✅ **All working correctly if**:

1. Server appears in Claude's available tools
2. "List all available MCP servers" shows your servers
3. "Generate tools" creates files in mcp_tools/
4. "Execute code" runs and returns output
5. No errors in Claude Desktop logs

## Quick Fix Commands

If you need to reinstall:

```bash
cd /home/ty/Repositories/ai_workspace/mcp_coordinator
source .venv/bin/activate
uv pip install -e .
```

If server won't start:

```bash
cd /home/ty/Repositories/ai_workspace/mcp_coordinator
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e .
```

## File Locations

| File | Path |
|------|------|
| Server code | `src/mcp_coordinator/server.py` |
| Claude config | `~/.config/Claude/claude_desktop_config.json` |
| MCP servers config | `mcp_servers.json` (in repo root) |
| Generated tools | `mcp_tools/` (in repo root) |
| Virtual env | `.venv/` (in repo root) |

## Expected Log Messages

When working correctly, you should see in Claude logs:

```
[mcp-coordinator] [info] Server started and connected successfully
[mcp-coordinator] [info] Message from client: {"method":"initialize"...}
```

**NOT** this (the old error):
```
<coroutine object main at 0x...>
RuntimeWarning: coroutine 'main' was never awaited
```

## Summary

**Status**: ✅ Fixed and ready  
**Files changed**: 1 (server.py completed)  
**Docs created**: 4 (guides and examples)  
**Action needed**: Update Claude config and restart

---

## Final Check

Run this command to verify everything:

```bash
cd /home/ty/Repositories/ai_workspace/mcp_coordinator && \
source .venv/bin/activate && \
python -c "
from mcp_coordinator.server import main
import inspect
print('✅ server.py: OK')
print(f'✅ main() function: {\"async\" if inspect.iscoroutinefunction(main) else \"sync\"}')
print(f'✅ File has {len(open(\"src/mcp_coordinator/server.py\").readlines())} lines')
" && \
echo "✅ All checks passed!"
```

**Expected output**:
```
✅ server.py: OK
✅ main() function: sync
✅ File has 174 lines
✅ All checks passed!
```

If you see this, **you're ready to restart Claude Desktop!**
