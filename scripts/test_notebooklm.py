#!/usr/bin/env python
"""Test NotebookLM MCP integration."""

import asyncio

from mcp_tools import notebooklm


async def main():
    notebook_url = "https://notebooklm.google.com/notebook/c8979a85-d6d3-4308-8046-adc910f7d244"

    print("Testing NotebookLM MCP tools...")
    print(f"Notebook URL: {notebook_url}\n")

    # Test asking a question to the notebook
    question = "What is the main topic of this notebook?"

    print(f"Asking question: '{question}'")
    print("=" * 60)

    try:
        result = await notebooklm.ask_question(question=question, notebook_url=notebook_url)

        print("\n✓ Successfully called NotebookLM!")
        print("\nResult:")
        print(result)

    except Exception as e:
        print(f"\n✗ Error calling NotebookLM: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
