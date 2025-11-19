#!/bin/bash
# Setup script for MCP Coordinator
# Run this to set up the venv and install dependencies

set -e

echo "🚀 Setting up MCP Coordinator..."
echo

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create venv
echo "📦 Creating virtual environment..."
uv venv

# Activate venv
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -e .

echo
echo "✅ Setup complete!"
echo
echo "Next steps:"
echo "1. Activate the venv: source .venv/bin/activate"
echo "2. Test the server: uv run mcp-coordinator-server --help"
echo "3. Add to your Claude config (see QUICK_START.md)"
echo
