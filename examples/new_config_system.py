"""
Example: Using MCP-Coordinator with New Configuration System

Demonstrates:
1. Project-local mcp.json configuration
2. Environment-based configuration
3. Ollama integration (cheapest option)
4. Docker executor (best security)
5. Cloud models (Ollama cloud)
"""

import asyncio
from pathlib import Path

from mcp_coordinator import Coordinator
from mcp_coordinator.config import ConfigManager, create_default_env_file
from mcp_coordinator.smol_executor import AgentExecutor, create_executor

# ==============================================================================
# Example 1: Basic Setup with Project-Local mcp.json
# ==============================================================================


async def example_basic():
    """Use default configuration (./mcp.json in project root)."""
    print("\n=== Example 1: Basic Setup ===\n")

    # Coordinator automatically looks for ./mcp.json
    # No need to specify path!
    coordinator = Coordinator()

    # Generate tool libraries
    await coordinator.generate_tools()

    # List available servers
    servers = await coordinator.list_servers()
    print(f"Available servers: {servers}")

    # Execute code using MCP tools
    code = """
from mcp_tools.chroma import list_collections

collections = list_collections()
print(f"Collections: {collections}")
"""

    result = await coordinator.execute_code(code)
    print(f"Result: {result}")

    await coordinator.close()


# ==============================================================================
# Example 2: Using MCP_JSON Environment Variable
# ==============================================================================


async def example_env_config():
    """Use MCP_JSON environment variable to point to config."""
    print("\n=== Example 2: Environment Variable Configuration ===\n")

    # Set MCP_JSON in your .env file:
    # MCP_JSON=/path/to/your/mcp_servers.json

    # ConfigManager automatically reads from .env
    config_mgr = ConfigManager()
    config_path = config_mgr.get_config_path()

    print(f"Using config: {config_path}")

    coordinator = Coordinator()
    await coordinator.generate_tools()

    await coordinator.close()


# ==============================================================================
# Example 3: Using Ollama with Local Models (Cheapest Option)
# ==============================================================================


async def example_ollama_local():
    """Use Ollama with local models for cheap, fast execution."""
    print("\n=== Example 3: Ollama Local Models ===\n")

    # Configure in .env:
    # OLLAMA_API_BASE=http://localhost:11434
    # OLLAMA_MODEL=llama3.2:3b

    # Create agent with Ollama
    agent = AgentExecutor(
        executor_type="local",
        model_provider="ollama",
    )

    # Run agent task
    response = agent.run("Calculate the 10th Fibonacci number")
    print(f"Agent response: {response}")

    agent.cleanup()


# ==============================================================================
# Example 4: Using Ollama Cloud Models (Scalable)
# ==============================================================================


async def example_ollama_cloud():
    """Use Ollama cloud models for larger, more capable models."""
    print("\n=== Example 4: Ollama Cloud Models ===\n")

    # First, authenticate with Ollama:
    # $ ollama signin

    # Then pull cloud model:
    # $ ollama pull qwen3-coder:480b-cloud

    # Configure in .env:
    # OLLAMA_MODEL=qwen3-coder:480b-cloud

    config_mgr = ConfigManager()
    ollama_config = config_mgr.get_ollama_config()

    print(f"Using Ollama cloud model: {ollama_config['model_id']}")
    print(f"API base: {ollama_config['api_base']}")

    # Cloud models work just like local ones!
    agent = AgentExecutor(
        executor_type="docker",  # Use Docker for better security
        model_provider="ollama",
    )

    response = agent.run("Write a Python function to generate prime numbers efficiently")
    print(f"Agent response: {response}")

    agent.cleanup()


# ==============================================================================
# Example 5: Using Docker Executor (Best Security/Performance)
# ==============================================================================


async def example_docker_executor():
    """Use Docker executor for secure, isolated code execution."""
    print("\n=== Example 5: Docker Executor ===\n")

    # Configure in .env:
    # MCP_EXECUTOR_TYPE=docker
    # DOCKER_IMAGE=python:3.12-slim
    # DOCKER_MEM_LIMIT=512m
    # DOCKER_CPU_QUOTA=50000

    # Create executor (reads config from .env)
    executor = create_executor(executor_type="docker")

    # Execute code in Docker container
    code = """
import math

def calculate_pi_leibniz(n_terms):
    pi = 0
    for i in range(n_terms):
        pi += ((-1)**i) / (2*i + 1)
    return pi * 4

result = calculate_pi_leibniz(100000)
print(f"Pi approximation: {result}")
result
"""

    result = executor.execute(code)
    print(f"Docker execution result: {result}")

    executor.cleanup()


# ==============================================================================
# Example 6: Complete Workflow with Multiple Executors
# ==============================================================================


async def example_complete_workflow():
    """Complete workflow using all features together."""
    print("\n=== Example 6: Complete Workflow ===\n")

    # 1. Initialize coordinator
    coordinator = Coordinator()
    await coordinator.generate_tools()

    # 2. Use Ollama for cheap local processing
    print("Step 1: Using Ollama for initial analysis...")
    local_agent = AgentExecutor(
        executor_type="local",
        model_provider="ollama",
    )

    analysis = local_agent.run("Analyze the computational complexity of binary search")
    print(f"Local analysis: {analysis[:100]}...")

    # 3. Use Docker executor for secure code execution
    print("\nStep 2: Running secure code execution in Docker...")
    docker_executor = create_executor(executor_type="docker")

    code = """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

# Test it
test_array = list(range(1, 1001))
result = binary_search(test_array, 500)
print(f"Found 500 at index: {result}")
result
"""

    result = docker_executor.execute(code)
    print(f"Execution result: {result}")

    # Cleanup
    local_agent.cleanup()
    docker_executor.cleanup()
    await coordinator.close()


# ==============================================================================
# Example 7: Creating Default Configuration Files
# ==============================================================================


def example_create_config():
    """Create default configuration files for a new project."""
    print("\n=== Example 7: Creating Configuration Files ===\n")

    project_root = Path.cwd()

    # Create .env file with defaults
    create_default_env_file(project_root)

    # Create default mcp.json
    mcp_json = project_root / "mcp.json"
    if not mcp_json.exists():
        mcp_config = {"mcpServers": {"chroma": {"command": "uvx", "args": ["chroma-mcp"], "env": {}}, "filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "./workspace"], "env": {}}}}

        import json

        mcp_json.write_text(json.dumps(mcp_config, indent=2))
        print(f"✓ Created {mcp_json}")

    print("\nConfiguration files created!")
    print("Edit .env to customize your setup")
    print("Edit mcp.json to add your MCP servers")


# ==============================================================================
# Main
# ==============================================================================


async def main():
    """Run all examples."""
    print("=" * 80)
    print("MCP-Coordinator: New Configuration System Examples")
    print("=" * 80)

    # Create default config files
    example_create_config()

    # Basic examples
    await example_basic()
    await example_env_config()

    # Ollama examples
    await example_ollama_local()
    # await example_ollama_cloud()  # Uncomment if you have cloud models

    # Docker example
    # await example_docker_executor()  # Uncomment if Docker is installed

    # Complete workflow
    # await example_complete_workflow()  # Uncomment to run full workflow

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
