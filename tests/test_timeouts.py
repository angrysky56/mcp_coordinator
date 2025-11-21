import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from mcp_coordinator.discovery import discover_all_servers, ServerIntrospector
from mcp_coordinator.core.client import McpClientManager, ConnectionState
from mcp_coordinator.core.config import ServerConfig


class TestTimeouts(unittest.IsolatedAsyncioTestCase):
    async def test_discovery_timeout(self):
        """Test that discovery times out for slow servers."""
        # Mock ConfigLoader to return a single server config
        with patch("mcp_coordinator.discovery.ConfigLoader") as mock_loader:
            mock_loader.load_from_json.return_value = {"slow-server": MagicMock(name="slow-server", transport_type="stdio", command="echo", args=[])}

            # Mock ServerIntrospector to sleep longer than timeout
            with patch("mcp_coordinator.discovery.ServerIntrospector") as mock_introspector_cls:
                mock_introspector = mock_introspector_cls.return_value

                async def slow_discover():
                    await asyncio.sleep(2)  # Sleep 2s
                    return {"tools": {}}

                mock_introspector.discover_tools = AsyncMock(side_effect=slow_discover)

                # Mock ConfigManager to return short timeout
                with patch("mcp_coordinator.config.ConfigManager") as mock_config_manager_cls:
                    mock_config_manager = mock_config_manager_cls.return_value
                    mock_config_manager.get_timeouts.return_value = {
                        "discovery": 0.1,  # Short timeout
                        "connect": 0.1,
                        "read": 0.1,
                    }

                    # Run discovery
                    results = await discover_all_servers(Path("dummy.json"))

                    # Verify result contains error
                    self.assertIn("slow-server", results)
                    self.assertIn("error", results["slow-server"])
                    self.assertIn("Discovery timed out", results["slow-server"]["error"])
                    print("✓ Discovery timeout verification passed")

    async def test_read_timeout(self):
        """Test that tool execution times out."""
        manager = McpClientManager()
        manager.connect_timeout = 2.0  # Long enough for connection
        manager.read_timeout = 0.1  # Short read timeout

        # Mock config
        mock_config = MagicMock()
        mock_server_config = ServerConfig(type="stdio", command="echo", args=[])
        mock_config.get_server.return_value = mock_server_config
        manager.config = mock_config
        manager.state = ConnectionState.INITIALIZED

        # Mock _connect_stdio to return immediately
        async def fast_connect(*args, **kwargs):
            session = MagicMock()

            async def slow_tool(*args, **kwargs):
                await asyncio.sleep(1)
                return "result"

            session.call_tool = AsyncMock(side_effect=slow_tool)
            return session

        with patch.object(manager, "_connect_stdio", side_effect=fast_connect):
            with self.assertRaises(TimeoutError):
                await manager.call_tool("slow-server", "some-tool")

        print("✓ Read timeout verification passed")

    async def test_connect_timeout(self):
        """Test that connection times out."""
        manager = McpClientManager()
        manager.connect_timeout = 0.1

        # Mock config
        mock_config = MagicMock()
        mock_server_config = ServerConfig(type="stdio", command="sleep", args=["10"])
        mock_config.get_server.return_value = mock_server_config
        manager.config = mock_config
        manager.state = ConnectionState.INITIALIZED

        # Mock stdio_client to hang
        # We need to mock the context manager returned by stdio_client
        with patch("mcp_coordinator.core.client.stdio_client") as mock_stdio:

            async def slow_enter(*args, **kwargs):
                await asyncio.sleep(1)
                return (MagicMock(), MagicMock())

            mock_ctx = MagicMock()
            mock_ctx.__aenter__ = AsyncMock(side_effect=slow_enter)
            mock_stdio.return_value = mock_ctx

            with self.assertRaises(TimeoutError):
                await manager.call_tool("slow-server", "some-tool")

        print("✓ Connection timeout verification passed")


if __name__ == "__main__":
    unittest.main()
