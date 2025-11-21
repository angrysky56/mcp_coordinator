import asyncio
import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path.cwd() / "src"))

from mcp_coordinator.config import ConfigManager
from mcp_coordinator.discovery import discover_all_servers


async def main():
    print(f"Current CWD: {Path.cwd()}")
    print(f"Current PATH: {os.environ.get('PATH')}")

    try:
        # Try to find uvx directly
        import shutil

        uvx_path = shutil.which("uvx")
        print(f"shutil.which('uvx'): {uvx_path}")
    except Exception as e:
        print(f"Error checking uvx: {e}")

    print("\n--- Starting Discovery ---")
    try:
        config_manager = ConfigManager()
        config_path = config_manager.get_config_path()
        print(f"Using config: {config_path}")

        results = await discover_all_servers(config_path)

        print("\n--- Results ---")
        for name, info in results.items():
            if "error" in info:
                print(f"❌ {name}: {info['error']}")
            else:
                print(f"✅ {name}: Found {len(info.get('tools', {}))} tools")

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
