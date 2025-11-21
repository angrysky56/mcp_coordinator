"""
Configuration management for MCP-Coordinator.

Handles loading MCP server configuration from:
1. Explicit path parameter
2. MCP_JSON environment variable
3. .env file in project root
4. ./mcp.json in project root (default)
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


class ConfigManager:
    """
    Manages MCP server configuration with multiple loading strategies.

    Priority order:
    1. Explicit config_path parameter
    2. MCP_JSON environment variable
    3. mcp_servers.json in project root
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """
        Initialize configuration manager.

        Args:
            project_root: Root directory of the project (defaults to cwd)
        """
        self.project_root = project_root or Path.cwd()

        # Load .env file from project root if it exists
        env_file = self.project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)

    def get_config_path(self, explicit_path: str | Path | None = None) -> Path:
        """
        Resolve configuration file path using priority order.

        Args:
            explicit_path: Explicitly provided config path (highest priority)

        Returns:
            Resolved Path to configuration file

        Raises:
            FileNotFoundError: If no configuration file found
        """
        # 1. Explicit path parameter (highest priority)
        if explicit_path is not None:
            path = Path(explicit_path).expanduser().resolve()
            if not path.exists():
                raise FileNotFoundError(f"Explicitly provided config file not found: {path}")
            return path

        # 2. MCP_JSON or MCP_SERVERS_CONFIG environment variable
        mcp_json_env = os.getenv("MCP_JSON") or os.getenv("MCP_SERVERS_CONFIG")
        if mcp_json_env:
            path = Path(mcp_json_env).expanduser().resolve()
            if not path.exists():
                raise FileNotFoundError(f"Environment variable points to non-existent file: {path}")
            return path

        # 3. mcp.json or mcp_servers.json in project root (default)
        for filename in ["mcp.json", "mcp_servers.json"]:
            default_path = self.project_root / filename
            if default_path.exists():
                return default_path

        # No configuration found
        raise FileNotFoundError(f"No MCP configuration found. Tried:\n  - MCP_JSON environment variable (not set)\n  - {default_path} (not found)\n\nPlease create mcp.json in your project root or set MCP_JSON environment variable.")

    def get_executor_type(self) -> str:
        """
        Get executor type from environment or use default.

        Returns:
            Executor type: 'local', 'docker', 'e2b', 'modal', or 'wasm'
        """
        return os.getenv("MCP_EXECUTOR_TYPE", "local")

    def get_ollama_config(self) -> dict[str, Any]:
        """
        Get Ollama configuration from environment.

        Returns:
            Dictionary with Ollama configuration
        """
        return {
            "api_base": os.getenv("OLLAMA_API_BASE", "http://localhost:11434"),
            "model_id": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        }

    def get_docker_config(self) -> dict[str, Any]:
        """
        Get Docker executor configuration from environment.

        Returns:
            Dictionary with Docker configuration
        """
        return {
            "image": os.getenv("DOCKER_IMAGE", "python:3.12-slim"),
            "mem_limit": os.getenv("DOCKER_MEM_LIMIT", "512m"),
            "cpu_quota": int(os.getenv("DOCKER_CPU_QUOTA", "50000")),
        }

    def get_timeouts(self) -> dict[str, float]:
        """
        Get timeout configuration.

        Returns:
            Dictionary with timeout values in seconds
        """
        return {
            "connect": float(os.getenv("MCP_CONNECT_TIMEOUT", "10.0")),
            "read": float(os.getenv("MCP_READ_TIMEOUT", "60.0")),
            "discovery": float(os.getenv("MCP_DISCOVERY_TIMEOUT", "30.0")),
        }


def create_default_env_file(project_root: Path) -> None:
    """
    Create a default .env file with example configuration.

    Args:
        project_root: Root directory of the project
    """
    env_file = project_root / ".env"

    if env_file.exists():
        print(f"⚠️  .env file already exists at {env_file}")
        return

    env_content = """# MCP-Coordinator Configuration
# =============================

# Path to MCP server configuration (optional, defaults to ./mcp.json)
# MCP_JSON=/path/to/your/mcp_servers.json

# Code executor type: local, docker, e2b, modal, wasm
# Recommended: docker (best security/performance balance)
MCP_EXECUTOR_TYPE=local

# Ollama Configuration (for cheapest local LLM option)
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Docker Executor Configuration (when MCP_EXECUTOR_TYPE=docker)
DOCKER_IMAGE=python:3.12-slim
DOCKER_MEM_LIMIT=512m
DOCKER_CPU_QUOTA=50000

# Optional: HuggingFace token for cloud models
# HF_TOKEN=your_token_here

# Optional: E2B API key (when MCP_EXECUTOR_TYPE=e2b)
# E2B_API_KEY=your_key_here

# Optional: Modal API token (when MCP_EXECUTOR_TYPE=modal)
# MODAL_TOKEN_ID=your_token_id
# MODAL_TOKEN_SECRET=your_token_secret
"""

    env_file.write_text(env_content)
    print(f"✓ Created default .env file at {env_file}")
    print("  Edit this file to configure MCP-Coordinator for your setup")
