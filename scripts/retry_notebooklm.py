#!/usr/bin/env python
"""Ask NotebookLM again with the existing session."""

import asyncio

from mcp_tools import notebooklm


async def main():
    # Use the same session ID from before
    session_id = "e1c58728"
    notebook_url = "https://notebooklm.google.com/notebook/c8979a85-d6d3-4308-8046-adc910f7d244"

    question = "What are the main topics and key concepts covered in this notebook? Please provide a comprehensive summary."

    print(f"Asking with session {session_id}:")
    print(f"'{question}'")
    print("=" * 60)

    try:
        result = await notebooklm.ask_question(question=question, session_id=session_id, notebook_url=notebook_url)

        print("\n✓ Result:")
        print(result)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
