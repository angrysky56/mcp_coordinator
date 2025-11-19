# MCP-Coordinator v0.2.0 - Configuration System Overhaul

## Summary

Complete refactor of MCP-Coordinator's configuration system, replacing auto-discovery with explicit project-local configuration and adding comprehensive support for smolagents' Docker executor and Ollama models (local and cloud).

## Key Changes

### 1. Configuration System

**Before (v0.1.0):**
- Auto-discovered Claude Desktop configs from system paths
- Implicit, unclear configuration priority
- No environment variable support
- Required config in known system locations

**After (v0.2.0):**
- **No auto-discovery** - Explicit configuration required
- **Project-local by default** - Uses `./mcp.json` in project root
- **Environment variables** - Full `.env` file support via `python-dotenv`
- **Clear priority order**: Explicit path > `MCP_JSON` env > `./mcp.json`

**Configuration Priority:**
```
1. Coordinator(config_path="/explicit/path.json")  # Highest
2. export MCP_JSON=/path/via/env.json
3. ./mcp.json in project root                      # Default
4. FileNotFoundError with helpful message          # None found
```

### 2. New Configuration Manager

**New File:** `src/mcp_coordinator/config.py`

```python
from mcp_coordinator.config import ConfigManager

config_mgr = ConfigManager(project_root=Path.cwd())

# Resolve config path (respects priority order)
config_path = config_mgr.get_config_path()

# Get executor configuration
executor_type = config_mgr.get_executor_type()  # from MCP_EXECUTOR_TYPE

# Get Ollama settings
ollama_config = config_mgr.get_ollama_config()  # from OLLAMA_* vars

# Get Docker settings
docker_config = config_mgr.get_docker_config()  # from DOCKER_* vars
```

### 3. Enhanced Executor System

**New File:** `src/mcp_coordinator/smol_executor.py`

Comprehensive smolagents integration with multiple backends:

| Executor | Best For | Security | Setup | Cost |
|----------|----------|----------|-------|------|
| **local** | Development | Basic | Easy | Free |
| **docker** | Production | Strong | Moderate | Free |
| **e2b** | Cloud execution | Strong | Easy | Paid |
| **modal** | Serverless | Strong | Easy | Paid |
| **wasm** | Browser/portable | Good | Moderate | Free |

**Usage:**
```python
from mcp_coordinator.smol_executor import create_executor, AgentExecutor

# Simple code execution
executor = create_executor(executor_type="docker")
result = executor.execute("print('Hello from Docker!')")

# Agent with LLM (Ollama)
agent = AgentExecutor(
    executor_type="docker",
    model_provider="ollama",
)
response = agent.run("Calculate Fibonacci(50)")
```

### 4. Ollama Integration

Full support for Ollama models (local and cloud):

**Local Models (Free):**
```bash
# .env
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

**Cloud Models (Scalable):**
```bash
# Authenticate once
ollama signin

# Pull cloud model
ollama pull qwen3-coder:480b-cloud

# .env
OLLAMA_MODEL=qwen3-coder:480b-cloud
```

Available cloud models:
- `qwen3-coder:480b-cloud` - 480B coding specialist
- `gpt-oss:120b-cloud` - 120B general purpose
- `gpt-oss:20b-cloud` - 20B balanced
- `deepseek-v3.1:671b-cloud` - 671B massive scale

**Code stays identical:**
```python
agent = AgentExecutor(model_provider="ollama")
response = agent.run(task)  # Runs locally or in cloud!
```

### 5. Docker Executor (Recommended)

Best balance of security and performance:

```bash
# .env
MCP_EXECUTOR_TYPE=docker
DOCKER_IMAGE=python:3.12-slim
DOCKER_MEM_LIMIT=512m
DOCKER_CPU_QUOTA=50000
```

**Features:**
- ✅ Container isolation
- ✅ Resource limits (CPU, memory)
- ✅ Network isolation possible
- ✅ Production-ready
- ✅ No cloud dependencies

**Automatic cleanup:**
```python
with executor:
    result = executor.execute(code)
# Container cleaned up automatically
```

### 6. Environment Variable Support

**New File:** `.env.example`

Complete environment-based configuration:

```bash
# Core
MCP_JSON=/path/to/mcp_servers.json
MCP_EXECUTOR_TYPE=docker

# Ollama (cheapest local option)
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Docker
DOCKER_IMAGE=python:3.12-slim
DOCKER_MEM_LIMIT=512m
DOCKER_CPU_QUOTA=50000

# Cloud services (optional)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
E2B_API_KEY=your_key_here
MODAL_TOKEN_ID=your_id
MODAL_TOKEN_SECRET=your_secret
```

### 7. Updated Dependencies

**pyproject.toml changes:**
```toml
dependencies = [
    "smolagents>=1.0.0",      # Updated from 0.1.0
    "python-dotenv>=1.0.0",   # NEW - .env support
    "litellm>=1.50.0",        # NEW - Universal LLM API
]

[project.optional-dependencies]
docker = ["docker>=7.0.0"]    # NEW
e2b = ["e2b-code-interpreter>=1.0.0"]  # NEW
modal = ["modal>=0.70.0"]     # NEW
```

## Breaking Changes

### 1. No Auto-Discovery

**Before:**
```python
coordinator = Coordinator()  # Auto-discovered system configs
```

**After:**
```python
coordinator = Coordinator()  # Uses ./mcp.json (explicit)

# OR set MCP_JSON env var
# OR provide explicit path
coordinator = Coordinator(config_path="/path/to/config.json")
```

**Migration:**
```bash
# Copy existing config to project root
cp ~/.config/claude/mcp_servers.json ./mcp.json
```

### 2. ConfigLoader.discover_claude_config() Removed

**Before:**
```python
from mcp_coordinator.discovery import ConfigLoader

path = ConfigLoader.discover_claude_config()  # Auto-discovery
```

**After:**
```python
from mcp_coordinator.config import ConfigManager

config_mgr = ConfigManager()
path = config_mgr.get_config_path()  # Explicit resolution
```

### 3. discover_all_servers() Requires Path

**Before:**
```python
servers = await discover_all_servers()  # Auto-discovered
```

**After:**
```python
servers = await discover_all_servers(config_path)  # Explicit path required
```

### 4. Executor Changes

**Old executor still works** but new `smol_executor` is recommended:

```python
# Old (still works)
from mcp_coordinator.executor import SecureExecutor
executor = SecureExecutor()

# New (recommended)
from mcp_coordinator.smol_executor import create_executor
executor = create_executor(executor_type="docker")
```

## New Features

### 1. Multiple Executor Backends

```python
# Local (fast development)
executor = create_executor("local")

# Docker (recommended production)
executor = create_executor("docker")

# E2B (cloud managed)
executor = create_executor("e2b")

# Modal (serverless)
executor = create_executor("modal")

# WASM (portable)
executor = create_executor("wasm")
```

### 2. Agent Execution with LLMs

```python
from mcp_coordinator.smol_executor import AgentExecutor

# Ollama local
agent = AgentExecutor(
    executor_type="docker",
    model_provider="ollama",
)

# OpenAI
agent = AgentExecutor(
    executor_type="docker",
    model_provider="openai/gpt-4",
)

# Anthropic
agent = AgentExecutor(
    executor_type="docker",
    model_provider="anthropic/claude-3-opus",
)

response = agent.run("Your task here")
```

### 3. Configuration Helpers

```python
from mcp_coordinator.config import create_default_env_file

# Create .env with sensible defaults
create_default_env_file(Path.cwd())
```

### 4. Comprehensive Examples

**New File:** `examples/new_config_system.py`

Shows:
- Project-local configuration
- Environment variable usage
- Ollama local and cloud models
- Docker executor
- Complete workflows
- Configuration file creation

## Documentation

### New Documents

1. **docs/CONFIGURATION.md** - Complete configuration guide
   - Priority system
   - Environment variables
   - Executor types comparison
   - Ollama integration
   - Migration guide
   - Best practices

### Updated Documents

1. **README.md** - Updated examples
2. **.env.example** - Comprehensive environment template

## Installation

### Basic
```bash
uv pip install mcp-coordinator
```

### With Docker (Recommended)
```bash
uv pip install 'mcp-coordinator[docker]'
```

### Complete (All Backends)
```bash
uv pip install 'mcp-coordinator[docker,e2b,modal]'
```

## Quick Start

```bash
# 1. Copy .env example
cp .env.example .env

# 2. Create mcp.json
cat > mcp.json << 'EOF'
{
  "mcpServers": {
    "chroma": {
      "command": "uvx",
      "args": ["chroma-mcp"]
    }
  }
}
EOF

# 3. Configure executor (in .env)
echo "MCP_EXECUTOR_TYPE=docker" >> .env
echo "OLLAMA_MODEL=llama3.2:3b" >> .env

# 4. Use it!
python examples/new_config_system.py
```

## Compatibility

- **Python:** 3.12+ (unchanged)
- **Operating Systems:** Linux, macOS, Windows
- **Docker:** Optional but recommended (for docker executor)
- **Ollama:** Optional (for Ollama models)

## Performance

| Executor | Startup | Throughput | Isolation | Overhead |
|----------|---------|------------|-----------|----------|
| local | <1ms | Highest | Basic | None |
| docker | ~100ms | High | Strong | Low |
| e2b | ~500ms | Medium | Strong | Network |
| modal | ~1s | Medium | Strong | Network |
| wasm | ~50ms | Medium | Good | Low |

## Security

### Executor Security Levels

1. **wasm** - Strongest (WASM sandbox)
2. **docker** - Strong (container isolation)
3. **e2b** - Strong (remote containers)
4. **modal** - Strong (cloud isolation)
5. **local** - Basic (LocalPythonExecutor sandbox)

### Recommendations

- **Development:** local executor
- **Production:** docker executor
- **Untrusted code:** docker, e2b, or wasm
- **Trusted environment:** local (fastest)

## Cost Comparison

| Option | Setup | Runtime | Scaling |
|--------|-------|---------|---------|
| Ollama Local | Free | Free | Limited by hardware |
| Ollama Cloud | Free | Free* | Unlimited |
| OpenAI | Free | Paid | Unlimited |
| Anthropic | Free | Paid | Unlimited |
| E2B | Free tier | Paid | Unlimited |
| Modal | Free tier | Paid | Unlimited |

*Ollama cloud is currently free in preview

**Recommendation:** Start with Ollama local (llama3.2:3b), scale to Ollama cloud (qwen3-coder:480b-cloud) as needed.

## Upgrade Path

### Immediate (No Breaking Changes)

Old code continues to work:
```python
coordinator = Coordinator()  # Still works if ./mcp.json exists
```

### Recommended (Full Features)

1. Copy config to project:
   ```bash
   cp ~/.config/claude/mcp_servers.json ./mcp.json
   ```

2. Create .env:
   ```bash
   cp .env.example .env
   # Edit as needed
   ```

3. Update code:
   ```python
   # Use new executor
   from mcp_coordinator.smol_executor import create_executor
   
   executor = create_executor("docker")
   ```

## Future Plans

- [ ] Skills persistence system (v0.3.0)
- [ ] Pre-built adapters for popular servers
- [ ] Kubernetes executor
- [ ] Enhanced caching for cloud models
- [ ] Tool composition framework

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- **Anthropic** - Code execution pattern inspiration
- **HuggingFace** - smolagents framework
- **Ollama** - Local and cloud model infrastructure
- **MCP Community** - Protocol and ecosystem

---

**Version:** 0.2.0  
**Date:** November 11, 2025  
**Breaking Changes:** Yes (configuration system)  
**Migration Required:** Copy mcp config to project root
