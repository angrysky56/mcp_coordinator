#!/usr/bin/env python
"""Test NotebookLM with your actual notebook."""

import asyncio
from mcp_tools.notebooklm import ask_question


async def main():
    notebook_url = "https://notebooklm.google.com/notebook/c8979a85-d6d3-4308-8046-adc910f7d244"

    print("🔍 Querying NotebookLM...")
    print(f"Notebook: {notebook_url}")
    print("=" * 80)

    # Ask a real question
    question = "What are the main topics and key information in this notebook? Provide a detailed summary of the content."

    print(f"\n📝 Question: {question}\n")
    print("⏳ Waiting for NotebookLM response...\n")

    try:
        result = await ask_question(question=question, notebook_url=notebook_url)

        print("✅ Response received!")
        print("=" * 80)

        # Parse the response
        import json

        if hasattr(result, "__iter__") and not isinstance(result, str):
            # It's a list of TextContent objects
            for item in result:
                if hasattr(item, "text"):
                    response_data = json.loads(item.text)

                    if response_data.get("success"):
                        data = response_data.get("data", {})
                        answer = data.get("answer", "")

                        print(f"\n📖 NotebookLM Answer:\n")
                        print(answer)
                        print("\n" + "=" * 80)
                        print(f"Session ID: {data.get('session_id')}")
                        print(f"Message count: {data.get('session_info', {}).get('message_count')}")
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
