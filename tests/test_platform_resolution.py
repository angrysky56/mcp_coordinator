import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from mcp_coordinator.core.client import McpClientManager


class TestPlatformResolution(unittest.TestCase):
    def setUp(self):
        self.manager = McpClientManager()

    @patch("sys.platform", "linux")
    @patch("pathlib.Path.home")
    @patch("shutil.which")
    def test_linux_resolution(self, mock_which, mock_home):
        """Test path resolution on Linux."""
        mock_home.return_value = Path("/home/user")
        mock_which.side_effect = lambda cmd, path=None: f"/resolved/{cmd}" if path and "/home/user/.local/bin" in path else None

        env = {"PATH": "/usr/bin"}
        resolved = self.manager._resolve_command("mytool", env)

        self.assertEqual(resolved, "/resolved/mytool")
        self.assertIn("/home/user/.local/bin", env["PATH"])
        self.assertIn("/home/user/.cargo/bin", env["PATH"])

    @patch("sys.platform", "win32")
    @patch("pathlib.Path.home")
    @patch("os.environ.get")
    @patch("shutil.which")
    def test_windows_resolution(self, mock_which, mock_env_get, mock_home):
        """Test path resolution on Windows."""
        mock_home.return_value = Path("C:\\Users\\User")

        def env_get(key, default=None):
            if key == "APPDATA":
                return "C:\\Users\\User\\AppData\\Roaming"
            if key == "LOCALAPPDATA":
                return "C:\\Users\\User\\AppData\\Local"
            return default

        mock_env_get.side_effect = env_get

        # Simulate finding tool in npm global path
        def which_side_effect(cmd, path=None):
            if path and "npm" in str(path):
                return f"C:\\Resolved\\{cmd}.exe"
            return None

        mock_which.side_effect = which_side_effect

        env = {"PATH": "C:\\Windows\\System32"}
        resolved = self.manager._resolve_command("mytool", env)

        self.assertEqual(resolved, "C:\\Resolved\\mytool.exe")
        self.assertIn("npm", env["PATH"])
        self.assertIn("AppData", env["PATH"])

    @patch("sys.platform", "darwin")
    @patch("pathlib.Path.home")
    @patch("shutil.which")
    def test_macos_resolution(self, mock_which, mock_home):
        """Test path resolution on macOS."""
        mock_home.return_value = Path("/Users/user")
        mock_which.side_effect = lambda cmd, path=None: f"/opt/homebrew/bin/{cmd}" if path and "/opt/homebrew/bin" in path else None

        env = {"PATH": "/usr/bin"}
        resolved = self.manager._resolve_command("brewtool", env)

        self.assertEqual(resolved, "/opt/homebrew/bin/brewtool")
        self.assertIn("/opt/homebrew/bin", env["PATH"])


if __name__ == "__main__":
    unittest.main()
