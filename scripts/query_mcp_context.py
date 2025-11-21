#!/usr/bin/env python
"""Query NotebookLM about giving LLMs context for MCP servers."""

import asyncio

from mcp_tools.notebooklm import ask_question


async def main():
    notebook_url = "https://notebooklm.google.com/notebook/92dd7b2b-c8a4-4a8b-8fa1-a3ddbebaec24"
    question = "How do I give an LLM proper context to use MCP servers effectively? What are the best practices for exposing MCP server capabilities to AI assistants?"

    print("🔍 Querying NotebookLM about MCP server context...")
    print("=" * 80)

    try:
        result = await ask_question(question=question, notebook_url=notebook_url)

        # Parse the response
        import json

        if hasattr(result, "__iter__") and not isinstance(result, str):
            for item in result:
                if hasattr(item, "text"):
                    response_data = json.loads(item.text)

                    if response_data.get("success"):
                        data = response_data.get("data", {})
                        answer = data.get("answer", "")

                        print("\n📖 Answer:\n")
                        print(answer)
                        print("\n" + "=" * 80)
                        print(f"Session ID: {data.get('session_id')}")
                    else:
                        print(f"❌ Error: {response_data.get('error')}")
        else:
            print(result)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
