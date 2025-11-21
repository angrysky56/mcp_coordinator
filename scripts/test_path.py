import os
import sys
import shutil
from pathlib import Path
from mcp_coordinator.discovery import ServerIntrospector, MCPServerConfig


def test_path_handling():
    # Simulate a config that uses npx
    config = MCPServerConfig(name="test-node", command="npx", args=["--version"])
    introspector = ServerIntrospector(config)

    # We want to inspect the env that would be passed to the subprocess
    # Since discover_tools does the work inside, we can inspect _resolve_command
    # and manually check what discover_tools does with PATH

    print(f"Current PATH: {os.environ.get('PATH')}")

    # Logic from discover_tools
    env = dict(os.environ)
    current_path = env.get("PATH", "")
    standard_paths = ["/usr/local/bin", "/usr/bin", "/bin"]
    for p in standard_paths:
        if p not in current_path.split(os.pathsep):
            current_path = f"{current_path}{os.pathsep}{p}" if current_path else p
    env["PATH"] = current_path

    print(f"Computed PATH in discover_tools: {env['PATH']}")

    # Check if NVM path is in there
    nvm_path = Path.home() / ".nvm" / "versions" / "node"
    found_nvm = False
    if nvm_path.exists():
        for version_dir in nvm_path.iterdir():
            if version_dir.is_dir() and str(version_dir / "bin") in env["PATH"]:
                found_nvm = True
                print(f"Found NVM path in env: {version_dir / 'bin'}")
                break

    if not found_nvm:
        print("FAILURE: NVM path NOT found in env['PATH']")
    else:
        print("SUCCESS: NVM path found in env['PATH']")

    # Check _resolve_command
    resolved = introspector._resolve_command("npx", env["PATH"])
    print(f"Resolved 'npx' to: {resolved}")

    if resolved and "nvm" in resolved and not found_nvm:
        print("CRITICAL: 'npx' resolved to NVM path, but NVM path is NOT in env['PATH']. This will cause 'node' not found error.")


if __name__ == "__main__":
    test_path_handling()
