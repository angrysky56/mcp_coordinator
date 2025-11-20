import asyncio
import json
import logging

from mcp_tools import arxiv_mcp_server

logging.basicConfig(level=logging.DEBUG)


async def main():
    print("Searching Arxiv for 'agentic coding'...")
    try:
        results = await arxiv_mcp_server.search_papers(query="agentic coding", max_results=3)

        # The tool returns a list of Content objects (TextContent, etc.)
        # We need to extract the text and parse it if it's JSON.
        if isinstance(results, list) and hasattr(results[0], "text"):
            print("Received list of Content objects. Extracting text...")
            full_text = "".join([r.text for r in results if hasattr(r, "text")])
            try:
                results = json.loads(full_text)
            except json.JSONDecodeError:
                print("Could not parse result as JSON. Raw text:")
                print(full_text)
                return

        if isinstance(results, list):
            print(f"Found {len(results)} papers.")
            for paper in results:
                if isinstance(paper, dict):
                    print(f"\nTitle: {paper.get('title', 'Unknown')}")
                    print(f"ID: {paper.get('id', 'Unknown')}")
                    summary = paper.get("summary", "")
                    print(f"Abstract: {summary[:150]}...")
                else:
                    print(f"Unexpected item type: {type(paper)}")
                    print(paper)
        else:
            print(f"Unexpected result type: {type(results)}")
            print(results)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
