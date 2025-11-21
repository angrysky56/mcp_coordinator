#!/usr/bin/env python
"""
Test execute_code and execute_file capabilities.
"""

import asyncio

from mcp_coordinator import Coordinator


async def test_execute_code():
    """Test code execution."""
    print("Testing execute_code...")
    print("=" * 60)

    test_code = """
# Test code execution
from mcp_tools import fetch

print("✓ mcp_tools imported successfully")
print(f"Available tools: {fetch.list_tools()}")

result = "Code execution works!"
print(f"Result: {result}")
"""

    async with Coordinator() as coord:
        result = await coord.execute_code(test_code)

        print("\n📊 Execution Result:")
        print(f"Status: {result.get('status', 'unknown')}")

        if result.get("stdout"):
            print(f"\nStdout:\n{result['stdout']}")

        if result.get("stderr"):
            print(f"\nStderr:\n{result['stderr']}")

        if result.get("error"):
            print(f"\nError:\n{result['error']}")

        print("=" * 60)


async def test_execute_file():
    """Test file execution."""
    print("\nTesting execute_file...")
    print("=" * 60)

    # Create a test file
    test_file = "/tmp/test_mcp_execution.py"
    test_content = """
from mcp_tools import chroma

print("✓ Executing from file")
print(f"Chroma tools: {chroma.list_tools()[:3]}")
"""

    with open(test_file, "w") as f:
        f.write(test_content)

    async with Coordinator() as coord:
        result = await coord.execute_file(test_file)

        print("\n📊 Execution Result:")
        print(f"Status: {result.get('status', 'unknown')}")

        if result.get("stdout"):
            print(f"\nStdout:\n{result['stdout']}")

        if result.get("stderr"):
            print(f"\nStderr:\n{result['stderr']}")

        if result.get("error"):
            print(f"\nError:\n{result['error']}")

        print("=" * 60)


async def main():
    print("MCP COORDINATOR EXECUTION TEST")
    print("=" * 60)

    await test_execute_code()
    await test_execute_file()

    print("\n✅ All execution tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
