#!/usr/bin/env python
"""Authenticate with NotebookLM."""

import asyncio

from mcp_tools import notebooklm


async def main():
    print("Setting up NotebookLM authentication...")
    print("=" * 60)
    print("A browser window will open for you to log in to Google.")
    print("You have up to 10 minutes to complete the login.")
    print("=" * 60)

    try:
        result = await notebooklm.setup_auth(show_browser=True)

        print("\n✓ Authentication setup initiated!")
        print("\nResult:")
        print(result)

        print("\n" + "=" * 60)
        print("Next step: Use get_health() to verify authentication")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during authentication setup: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
