#!/bin/bash
# Test the MCP Coordinator Server
# This script helps you verify the server is working correctly

set -e

echo "🧪 Testing MCP Coordinator Server..."
echo

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate venv
source .venv/bin/activate

echo "1️⃣ Testing server help..."
uv run mcp-coordinator-server --help
echo "✅ Help works!"
echo

echo "2️⃣ Testing server import..."
python -c "from mcp_coordinator.server import mcp; print('✅ Server imports correctly!')"
echo

echo "3️⃣ Available tools in the server:"
python -c "
from mcp_coordinator.server import mcp
print('Tools:')
for tool in mcp._tool_manager._tools.values():
    print(f'  - {tool.fn.__name__}: {tool.fn.__doc__.split(chr(10))[0] if tool.fn.__doc__ else \"\"}'
)
"
echo

echo "✅ All tests passed!"
echo
echo "Next steps:"
echo "1. Configure your mcp_servers.json"
echo "2. Add to Claude config (see QUICK_START.md)"
echo "3. Or test with MCP Inspector: mcp dev mcp-coordinator-server"
echo
