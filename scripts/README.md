# Scripts and Utilities

This directory contains utility scripts and testing tools for the MCP-Coordinator.

## Organization

### Core Utilities (Production-Ready)
- **`run_tool.py`** - Universal CLI tool runner for any MCP server
- **`inspect_tools.py`** - Tool schema introspection and documentation

### Testing & Development
- **`test_execution.py`** - Test execute_code/execute_file capabilities
- **`test_resources.py`** - Test MCP resources (servers://available, servers://summary)
- **`test_discovery.py`** - Test server discovery mechanism
- **`test_path.py`** - Test PATH resolution for executables
- **`debug_discovery.py`** - Debug server discovery with detailed logging

### NotebookLM Integration
- **`setup_notebooklm_auth.py`** - Initialize NotebookLM authentication
- **`verify_notebooklm.py`** - Verify NotebookLM auth and test query
- **`retry_notebooklm.py`** - Retry query with existing session
- **`test_notebooklm.py`** - Basic NotebookLM integration test
- **`test_notebooklm_full.py`** - Comprehensive NotebookLM test with parsing
- **`query_mcp_context.py`** - Query NotebookLM about MCP best practices

### Skills Development
- **`test_skills.py`** - Test skills creation and management

### Code Generation
- **`generate_adapters.py`** - Generate adapter code (if needed)

## Usage

All scripts should be run with `PYTHONPATH=src:.` from the project root:

```bash
# Example: Run a tool
PYTHONPATH=src:. .venv/bin/python scripts/run_tool.py fetch fetch url=https://example.com

# Example: Test resources
PYTHONPATH=src:. .venv/bin/python scripts/test_resources.py

# Example: Inspect tools
PYTHONPATH=src:. .venv/bin/python scripts/inspect_tools.py
```

## Development Workflow

1. **First time setup**: Run `setup_notebooklm_auth.py` if using NotebookLM
2. **Server discovery**: Use `test_discovery.py` to verify all servers are found
3. **Tool inspection**: Use `inspect_tools.py` to see what tools are available
4. **Direct testing**: Use `run_tool.py` to test individual tools
5. **Execution testing**: Use `test_execution.py` to verify code execution works

## Cleanup

Most test scripts here were created during development and debugging. They remain useful for:
- Verifying functionality after changes
- Understanding how to use the coordinator
- Debugging issues with specific servers
- Teaching examples for new contributors
