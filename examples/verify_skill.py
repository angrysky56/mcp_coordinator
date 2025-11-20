import asyncio
import logging

from skills.research import research_topic

logging.basicConfig(level=logging.INFO)


async def main():
    print("Verifying research_topic skill...")
    papers = await research_topic("agentic coding", max_results=3)

    if papers:
        print(f"✓ Successfully retrieved {len(papers)} papers")
        for p in papers:
            print(f"- {p.get('title', 'Unknown')}")
    else:
        print("✗ No papers returned or error occurred")


if __name__ == "__main__":
    asyncio.run(main())
