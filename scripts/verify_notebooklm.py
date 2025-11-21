#!/usr/bin/env python
"""Verify NotebookLM authentication and test query."""

import asyncio

from mcp_tools import notebooklm


async def main():
    print("Verifying NotebookLM authentication...")
    print("=" * 60)

    # Check health/auth status
    try:
        health = await notebooklm.get_health()
        print("✓ Health check result:")
        print(health)
        print()

    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return

    # Now try querying the notebook
    notebook_url = "https://notebooklm.google.com/notebook/c8979a85-d6d3-4308-8046-adc910f7d244"
    question = "What is the main topic covered in this notebook?"

    print("=" * 60)
    print(f"Asking: '{question}'")
    print(f"Notebook: {notebook_url}")
    print("=" * 60)

    try:
        result = await notebooklm.ask_question(question=question, notebook_url=notebook_url)

        print("\n✓ Query successful!")
        print("\nResult:")
        print(result)

    except Exception as e:
        print(f"\n✗ Query failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
