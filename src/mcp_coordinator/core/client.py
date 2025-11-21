"""MCP Client Manager with state machine architecture for lazy loading and connection.

This module provides the core runtime client manager that connects to MCP servers
on-demand, caches tools, and manages the lifecycle of server connections using
an explicit state machine.
"""

import asyncio
import logging
import os
from enum import Enum
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import Tool

from mcp_coordinator.config import ConfigManager

from .config import McpConfig, ServerConfig

logger = logging.getLogger("mcp_coordinator.core.client")


class ConnectionState(str, Enum):
    """Explicit states for the MCP Client Manager lifecycle.

    States:
        UNINITIALIZED: Manager created but not initialized
        INITIALIZED: Configuration loaded, no server connections
        CONNECTED: At least one server connection established
    """

    UNINITIALIZED = "uninitialized"
    INITIALIZED = "initialized"
    CONNECTED = "connected"


class McpClientManager:
    """Lazy-loading MCP client manager with explicit state machine.

    This manager implements a state machine pattern for managing MCP server
    connections with the following characteristics:

    1. Lazy Loading: Servers are only connected when their tools are first requested
    - Lazy initialization: Config loaded on initialize(), servers NOT connected
    - Lazy connection: Servers connect on first call_tool() call
    - Tool caching: Cache tools per server to avoid repeated list_tools calls
    - Defensive unwrapping: Handle response.value and fallback patterns
    - Explicit state tracking: Clear state transitions with validation

    State Transitions:
        UNINITIALIZED -> INITIALIZED (via initialize())
        INITIALIZED -> CONNECTED (via _connect_to_server())
        any state -> UNINITIALIZED (via cleanup())
    """

    def __init__(self) -> None:
        """Initialize an uninitialized MCP Client Manager."""
        self.state = ConnectionState.UNINITIALIZED
        self.config: McpConfig | None = None
        self.sessions: dict[str, ClientSession] = {}
        self.tools_cache: dict[str, list[Tool]] = {}

        # Context managers for manual lifecycle management
        self._stdio_contexts: dict[str, Any] = {}
        self._session_contexts: dict[str, Any] = {}
        self._read_streams: dict[str, Any] = {}
        self._write_streams: dict[str, Any] = {}

        # Load timeouts
        config_manager = ConfigManager()
        timeouts = config_manager.get_timeouts()
        self.connect_timeout = timeouts["connect"]
        self.read_timeout = timeouts["read"]

    def _validate_state(self, required_state: ConnectionState, operation: str) -> None:
        """Validate that the manager is in the required state."""
        if self.state != required_state:
            raise RuntimeError(f"Cannot {operation}: Manager is in state '{self.state.value}', but requires state '{required_state.value}'")

    def _validate_state_at_least(self, minimum_state: ConnectionState, operation: str) -> None:
        """Validate that the manager has at least reached the minimum state."""
        state_order = [
            ConnectionState.UNINITIALIZED,
            ConnectionState.INITIALIZED,
            ConnectionState.CONNECTED,
        ]
        current_idx = state_order.index(self.state)
        required_idx = state_order.index(minimum_state)

        if current_idx < required_idx:
            raise RuntimeError(f"Cannot {operation}: Manager is in state '{self.state.value}', but requires at least state '{minimum_state.value}'")

    def _mark_initialized(self) -> None:
        """Transition to INITIALIZED state."""
        self.state = ConnectionState.INITIALIZED
        logger.debug("State transition: UNINITIALIZED -> INITIALIZED")

    def _mark_connected(self) -> None:
        """Transition to CONNECTED state."""
        if self.state == ConnectionState.INITIALIZED:
            self.state = ConnectionState.CONNECTED
            logger.debug("State transition: INITIALIZED -> CONNECTED")

    def _mark_uninitialized(self) -> None:
        """Transition back to UNINITIALIZED state."""
        self.state = ConnectionState.UNINITIALIZED
        logger.debug("State transition: -> UNINITIALIZED")

    def initialize(self, config_path: Path | None = None) -> None:
        """Initialize the manager by loading configuration.

        Args:
            config_path: Path to mcp_config.json. If None, looks in default locations.
        """
        if self.state != ConnectionState.UNINITIALIZED:
            logger.warning("Manager already initialized, reloading config")

        # Load configuration
        if config_path:
            with open(config_path) as f:
                self.config = McpConfig.from_json(f.read())
        else:
            # Try default locations
            possible_paths = [
                Path("mcp.json"),
                Path("mcp_servers.json"),
                Path(os.getenv("MCP_JSON", "")),
            ]
            for path in possible_paths:
                if path and path.exists():
                    with open(path) as f:
                        self.config = McpConfig.from_json(f.read())
                    break

            if not self.config:
                raise FileNotFoundError("Could not find MCP configuration file")

        self._mark_initialized()

    async def _connect_to_server(self, server_name: str, server_config: ServerConfig) -> ClientSession:
        """Connect to a specific server."""
        if server_name in self.sessions:
            return self.sessions[server_name]

        logger.info(f"Connecting to server: {server_name} ({server_config.type})")

        try:
            if server_config.type == "stdio":
                session = await self._connect_stdio(server_name, server_config)
            elif server_config.type == "sse":
                session = await self._connect_sse(server_name, server_config)
            else:
                raise ValueError(f"Unsupported transport: {server_config.type}")

            self.sessions[server_name] = session
            self._mark_connected()
            return session

        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            # Cleanup partial connection
            await self._cleanup_server(server_name)
            raise

    def _resolve_command(self, command: str, env: dict[str, str]) -> str:
        """Resolve absolute path for a command, checking common user paths in a platform-agnostic way."""
        import shutil
        import sys

        # 1. Try with provided PATH
        path_env = env.get("PATH", os.environ.get("PATH", ""))
        resolved = shutil.which(command, path=path_env)
        if resolved:
            return resolved

        # 2. Try with common user paths based on platform
        home = Path.home()
        common_paths = []

        if sys.platform == "win32":
            # Windows specific paths
            appdata = os.environ.get("APPDATA")
            localappdata = os.environ.get("LOCALAPPDATA")

            if appdata:
                common_paths.append(Path(appdata) / "npm")  # npm global
            if localappdata:
                common_paths.append(Path(localappdata) / "Programs" / "Python" / "Scripts")  # Python scripts
                common_paths.append(Path(localappdata) / "uv")  # uv

            # Cargo bin is common on Windows too
            common_paths.append(home / ".cargo" / "bin")

        else:
            # Unix-like (Linux/macOS) paths
            common_paths.extend(
                [
                    home / ".pyenv" / "shims",
                    home / ".cargo" / "bin",
                    home / ".local" / "bin",
                    Path("/usr/local/bin"),
                    Path("/usr/bin"),
                    Path("/bin"),
                    Path("/opt/homebrew/bin"),  # macOS Homebrew
                ]
            )

            # Add NVM paths if they exist
            nvm_versions = home / ".nvm" / "versions" / "node"
            if nvm_versions.exists():
                for version_dir in nvm_versions.iterdir():
                    if version_dir.is_dir():
                        common_paths.append(version_dir / "bin")

        # Construct search path
        search_path = os.pathsep.join(str(p) for p in common_paths)

        # Update env PATH to include these
        current_path = env.get("PATH", "")
        if current_path:
            env["PATH"] = f"{search_path}{os.pathsep}{current_path}"
        else:
            env["PATH"] = search_path

        resolved = shutil.which(command, path=search_path)
        if resolved:
            return resolved

        # 3. Fallback to original command
        return command

    async def _connect_stdio(self, server_name: str, config: ServerConfig) -> ClientSession:
        """Connect using stdio transport."""
        if not config.command:
            raise ValueError(f"Server {server_name} missing command")

        # Prepare environment
        env = dict(os.environ)
        if config.env:
            env.update(config.env)

        # Resolve command and update PATH in env
        command = self._resolve_command(config.command, env)

        server_params = StdioServerParameters(
            command=command,
            args=config.args,
            env=env,
        )

        async def _connect():
            # Establish stdio connection and store context manager
            stdio_ctx = stdio_client(server_params)
            streams = await stdio_ctx.__aenter__()
            read_stream, write_stream = streams

            self._stdio_contexts[server_name] = stdio_ctx
            self._read_streams[server_name] = read_stream
            self._write_streams[server_name] = write_stream

            # Create and initialize session
            session = ClientSession(read_stream, write_stream)
            client = await session.__aenter__()

            self._session_contexts[server_name] = session

            await client.initialize()
            return client

        # Wrap connection in timeout
        try:
            return await asyncio.wait_for(_connect(), timeout=self.connect_timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Connection to {server_name} timed out after {self.connect_timeout}s")

    async def _connect_sse(self, server_name: str, config: ServerConfig) -> ClientSession:
        """Connect using SSE transport."""
        if not config.url:
            raise ValueError(f"Server {server_name} missing url")

        async def _connect():
            # Establish SSE connection
            sse_ctx = sse_client(url=config.url)
            streams = await sse_ctx.__aenter__()
            read_stream, write_stream = streams

            self._stdio_contexts[server_name] = sse_ctx
            self._read_streams[server_name] = read_stream
            self._write_streams[server_name] = write_stream

            # Create and initialize session
            session = ClientSession(read_stream, write_stream)
            client = await session.__aenter__()

            self._session_contexts[server_name] = session

            await client.initialize()
            return client

        # Wrap connection in timeout
        try:
            return await asyncio.wait_for(_connect(), timeout=self.connect_timeout)
        except TimeoutError:
            raise TimeoutError(f"Connection to {server_name} timed out after {self.connect_timeout}s")

    async def _cleanup_server(self, server_name: str) -> None:
        """Clean up resources for a specific server."""
        # Close session
        if server_name in self._session_contexts:
            try:
                await self._session_contexts[server_name].__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing session for {server_name}: {e}")
            del self._session_contexts[server_name]

        # Close transport
        if server_name in self._stdio_contexts:
            try:
                await self._stdio_contexts[server_name].__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing transport for {server_name}: {e}")
            del self._stdio_contexts[server_name]

        if server_name in self.sessions:
            del self.sessions[server_name]

        if server_name in self._read_streams:
            del self._read_streams[server_name]
        if server_name in self._write_streams:
            del self._write_streams[server_name]

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Call an MCP tool with lazy server connection."""
        self._validate_state_at_least(ConnectionState.INITIALIZED, "call_tool")

        if not self.config:
            raise RuntimeError("Configuration not loaded")

        server_config = self.config.get_server(server_name)
        if not server_config:
            raise ValueError(f"Server {server_name} not found in configuration")

        if server_config.disabled:
            raise ValueError(f"Server {server_name} is disabled")

        # Connect if needed
        session = await self._connect_to_server(server_name, server_config)

        # Call tool with timeout
        try:
            result = await asyncio.wait_for(session.call_tool(tool_name, arguments or {}), timeout=self.read_timeout)
        except TimeoutError:
            raise TimeoutError(f"Tool call {tool_name} on {server_name} timed out after {self.read_timeout}s")

        # Unwrap result similar to reference implementation
        if hasattr(result, "content"):
            return result.content
        return result

    async def list_tools(self, server_name: str) -> list[Tool]:
        """List tools for a server, using cache if available."""
        self._validate_state_at_least(ConnectionState.INITIALIZED, "list_tools")

        if server_name in self.tools_cache:
            return self.tools_cache[server_name]

        if not self.config:
            raise RuntimeError("Configuration not loaded")

        server_config = self.config.get_server(server_name)
        if not server_config:
            raise ValueError(f"Server {server_name} not found")

        # Connect if needed
        session = await self._connect_to_server(server_name, server_config)

        result = await session.list_tools()
        tools = result.tools

        self.tools_cache[server_name] = tools
        return tools

    async def cleanup(self) -> None:
        """Close all connections and reset manager."""
        logger.info("Cleaning up MCP Client Manager")

        # Close all sessions
        for server_name in list(self._session_contexts.keys()):
            try:
                await self._session_contexts[server_name].__aexit__(None, None, None)
            except Exception as e:
                # Ignore cancel scope errors that can occur when contexts are entered
                # and exited in different event loop tasks
                if "cancel scope" in str(e).lower() or isinstance(e, asyncio.CancelledError):
                    logger.debug(f"Ignoring cancel scope error for {server_name}: {e}")
                else:
                    logger.error(f"Error closing session for {server_name}: {e}")

        # Close all transports
        for server_name in list(self._stdio_contexts.keys()):
            try:
                await self._stdio_contexts[server_name].__aexit__(None, None, None)
            except Exception as e:
                # Ignore cancel scope errors that can occur when contexts are entered
                # and exited in different event loop tasks
                if "cancel scope" in str(e).lower() or isinstance(e, asyncio.CancelledError):
                    logger.debug(f"Ignoring cancel scope error for {server_name}: {e}")
                else:
                    logger.error(f"Error closing transport for {server_name}: {e}")

        self.sessions.clear()
        self.tools_cache.clear()
        self._session_contexts.clear()
        self._stdio_contexts.clear()
        self._read_streams.clear()
        self._write_streams.clear()

        self._mark_uninitialized()
