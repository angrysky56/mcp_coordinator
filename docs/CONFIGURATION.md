# Configuration Guide

## Overview

MCP-Coordinator uses a flexible, project-local configuration system that prioritizes:
1. **No auto-discovery** - Explicit configuration paths
2. **Environment variables** - Easy CI/CD and Docker integration
3. **Project-local defaults** - `mcp.json` in your project root

## Configuration Priority

MCP-Coordinator resolves configuration in this order:

```
1. Explicit config_path parameter (highest priority)
   └─> Coordinator(config_path="/custom/path.json")

2. MCP_JSON environment variable
   └─> export MCP_JSON=/path/to/mcp_servers.json

3. ./mcp.json in project root (default)
   └─> Automatically used if present

4. No configuration found
   └─> Raises FileNotFoundError with helpful message
```

## Quick Start

### 1. Create Configuration Files

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env

# Create mcp.json (or use existing one)
cat > mcp.json << 'EOF'
{
  "mcpServers": {
    "chroma": {
      "command": "uvx",
      "args": ["chroma-mcp"],
      "env": {}
    }
  }
}
EOF
```

### 2. Install Dependencies

```bash
# Basic installation
uv pip install mcp-coordinator

# With Docker support (recommended)
uv pip install 'mcp-coordinator[docker]'

# With all backends
uv pip install 'mcp-coordinator[docker,e2b,modal]'
```

### 3. Use the Coordinator

```python
from mcp_coordinator import Coordinator

# Automatically uses ./mcp.json
coordinator = Coordinator()

# Or specify explicit path
coordinator = Coordinator(config_path="/custom/path.json")
```

## Environment Variables

### Core Configuration

```bash
# Path to MCP server configuration
MCP_JSON=/path/to/mcp_servers.json  # Optional, defaults to ./mcp.json

# Executor type: local, docker, e2b, modal, wasm
MCP_EXECUTOR_TYPE=local  # Default: local, Recommended: docker
```

### Ollama Configuration (Cheapest Option)

```bash
# Ollama API endpoint
OLLAMA_API_BASE=http://localhost:11434

# Model selection
# Local models: llama3.2:3b, qwen2.5-coder:7b
# Cloud models: qwen3-coder:480b-cloud, gpt-oss:120b-cloud
OLLAMA_MODEL=llama3.2:3b
```

### Docker Configuration

```bash
# Docker executor settings (when MCP_EXECUTOR_TYPE=docker)
DOCKER_IMAGE=python:3.12-slim
DOCKER_MEM_LIMIT=512m
DOCKER_CPU_QUOTA=50000  # 50% of one core
```

### Cloud Services (Optional)

```bash
# HuggingFace (for hosted models)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# E2B (remote execution service)
E2B_API_KEY=your_e2b_key_here

# Modal (serverless execution)
MODAL_TOKEN_ID=your_token_id
MODAL_TOKEN_SECRET=your_token_secret
```

## Executor Types

### Local Executor (Default)

**Best for:** Development, prototyping, trusted environments

```python
from mcp_coordinator.smol_executor import create_executor

executor = create_executor(executor_type="local")
result = executor.execute("print('Hello, World!')")
```

**Features:**
- ✅ Fast (no container overhead)
- ✅ Simple setup
- ⚠️ Limited security (sandboxed Python only)
- ✅ Good for trusted code

### Docker Executor (Recommended)

**Best for:** Production, untrusted code, best security/performance balance

```python
executor = create_executor(executor_type="docker")
result = executor.execute("import requests; print(requests.__version__)")
```

**Features:**
- ✅ Strong isolation (container-based)
- ✅ Resource limits (CPU, memory)
- ✅ Network isolation possible
- ⚠️ Requires Docker installed
- ✅ Production-ready

**Setup:**
```bash
# Install Docker support
uv pip install 'mcp-coordinator[docker]'

# Configure in .env
MCP_EXECUTOR_TYPE=docker
DOCKER_IMAGE=python:3.12-slim
```

### E2B Executor

**Best for:** Managed cloud execution, no local Docker needed

```python
executor = create_executor(executor_type="e2b")
```

**Features:**
- ✅ Cloud-based (no local setup)
- ✅ Managed service
- ✅ Fast cold starts
- ⚠️ Requires E2B account
- ⚠️ Network latency

**Setup:**
```bash
uv pip install 'mcp-coordinator[e2b]'

# Get API key from https://e2b.dev/
export E2B_API_KEY=your_key_here
```

### Modal Executor

**Best for:** Serverless, scalable workloads

```python
executor = create_executor(executor_type="modal")
```

**Features:**
- ✅ Serverless (auto-scaling)
- ✅ GPU support available
- ✅ Pay-per-use
- ⚠️ Requires Modal account
- ⚠️ Cold start latency

### WASM Executor

**Best for:** Browser environments, portable execution

```python
executor = create_executor(executor_type="wasm")
```

**Features:**
- ✅ Browser-compatible
- ✅ Portable (Deno-based)
- ✅ Good isolation
- ⚠️ Requires Deno installed
- ⚠️ Limited package support

## Ollama Integration

### Local Models (Free)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2:3b

# Configure in .env
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

**Usage:**
```python
from mcp_coordinator.smol_executor import AgentExecutor

agent = AgentExecutor(
    executor_type="docker",
    model_provider="ollama",
)

response = agent.run("Calculate the 50th Fibonacci number")
print(response)
```

### Cloud Models (Scalable)

Ollama now offers cloud models for larger, more capable LLMs:

```bash
# Authenticate with Ollama
ollama signin

# Pull a cloud model (runs on Ollama's servers)
ollama pull qwen3-coder:480b-cloud

# Update .env
OLLAMA_MODEL=qwen3-coder:480b-cloud
```

**Available Cloud Models:**
- `qwen3-coder:480b-cloud` - Large coding model
- `gpt-oss:120b-cloud` - General purpose
- `gpt-oss:20b-cloud` - Balanced performance
- `deepseek-v3.1:671b-cloud` - Massive scale

**Usage is identical to local models:**
```python
# Just update your .env file - code stays the same!
agent = AgentExecutor(model_provider="ollama")
response = agent.run("Your task here")
```

## Configuration Examples

### Development Setup

`.env`:
```bash
MCP_EXECUTOR_TYPE=local
OLLAMA_MODEL=llama3.2:3b
```

`mcp.json`:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./workspace"]
    }
  }
}
```

### Production Setup

`.env`:
```bash
MCP_EXECUTOR_TYPE=docker
DOCKER_IMAGE=python:3.12-slim
DOCKER_MEM_LIMIT=512m
OLLAMA_MODEL=qwen3-coder:480b-cloud
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

### CI/CD Setup

```yaml
# .github/workflows/test.yml
env:
  MCP_JSON: ${{ secrets.MCP_CONFIG }}
  MCP_EXECUTOR_TYPE: docker
  OLLAMA_API_BASE: ${{ secrets.OLLAMA_URL }}
```

## Migration Guide

### From Old Auto-Discovery System

**Before:**
```python
# Old: Auto-discovered Claude config
coordinator = Coordinator()  # Searched ~/.config/claude/, etc.
```

**After:**
```python
# New: Explicit project-local config
coordinator = Coordinator()  # Uses ./mcp.json in project root

# Or specify path explicitly
coordinator = Coordinator(config_path="./mcp_servers.json")

# Or use environment variable
# export MCP_JSON=/path/to/config.json
coordinator = Coordinator()
```

### Updating Your Project

1. **Copy your MCP configuration to project root:**
   ```bash
   cp ~/.config/claude/mcp_servers.json ./mcp.json
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Update imports (if using old executor):**
   ```python
   # Old
   from mcp_coordinator.executor import SecureExecutor
   
   # New
   from mcp_coordinator.smol_executor import create_executor
   ```

4. **Update code:**
   ```python
   # Old
   coordinator = Coordinator()  # Auto-discovered
   
   # New - explicitly uses ./mcp.json
   coordinator = Coordinator()
   ```

## Best Practices

### 1. Use Docker in Production

```bash
MCP_EXECUTOR_TYPE=docker
DOCKER_IMAGE=python:3.12-slim
```

### 2. Start with Ollama Local, Scale to Cloud

```bash
# Development
OLLAMA_MODEL=llama3.2:3b

# Production
OLLAMA_MODEL=qwen3-coder:480b-cloud
```

### 3. Use Environment Variables for Secrets

```bash
# .env (gitignored)
HF_TOKEN=secret_value

# mcp.json (committed)
{
  "mcpServers": {
    "server": {
      "env": {
        "TOKEN": "${HF_TOKEN}"  # Reference env var
      }
    }
  }
}
```

### 4. Keep mcp.json Simple

```json
{
  "mcpServers": {
    "chroma": {
      "command": "uvx",
      "args": ["chroma-mcp"]
    }
  }
}
```

Configuration details go in `.env`, structure goes in `mcp.json`.

## Troubleshooting

### Configuration Not Found

```
FileNotFoundError: No MCP configuration found
```

**Solution:** Create `mcp.json` in project root or set `MCP_JSON` environment variable.

### Docker Connection Failed

```
Error: Cannot connect to Docker daemon
```

**Solution:** Start Docker service or use a different executor type.

### Ollama Connection Failed

```
Error: Connection refused to http://localhost:11434
```

**Solution:** Start Ollama service: `ollama serve`

### Import Errors

```
ImportError: smolagents[docker] not installed
```

**Solution:** Install with extras:
```bash
uv pip install 'mcp-coordinator[docker]'
```

## See Also

- [Examples](/examples/new_config_system.py) - Complete usage examples
- [Ollama Documentation](https://ollama.com/docs) - Ollama setup and models
- [smolagents Documentation](https://huggingface.co/docs/smolagents) - Executor details
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/) - Container security
