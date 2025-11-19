"""
Command-line interface for MCP-Coordinator.
"""

import argparse
import asyncio
from pathlib import Path

from rich.console import Console
from rich.table import Table

from mcp_coordinator.coordinator import Coordinator
from mcp_coordinator.skills import get_skills_manager


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="MCP-Coordinator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate tools command
    gen_parser = subparsers.add_parser("generate", help="Generate tool libraries")
    gen_parser.add_argument(
        "--config", type=Path, help="Path to MCP server config"
    )
    gen_parser.add_argument(
        "--force", action="store_true", help="Force regeneration"
    )

    # List servers command
    list_servers_parser = subparsers.add_parser("servers", help="List available servers")
    list_servers_parser.add_argument(
        "--config", type=Path, help="Path to MCP server config"
    )

    # List tools command
    list_tools_parser = subparsers.add_parser("tools", help="List tools for a server")
    list_tools_parser.add_argument("server", help="Name of the server")
    list_tools_parser.add_argument(
        "--config", type=Path, help="Path to MCP server config"
    )

    # List skills command
    list_skills_parser = subparsers.add_parser("skills", help="List available skills")

    # Search skills command
    search_skills_parser = subparsers.add_parser("search-skills", help="Search for skills")
    search_skills_parser.add_argument("query", help="Search query")

    return parser


async def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    console = Console()

    if args.command == "generate":
        console.print("[bold green]Generating tool libraries...[/bold green]")
        coordinator = Coordinator(config_path=args.config)
        await coordinator.generate_tools(force_refresh=args.force)
        console.print("[bold green]✓ Tool libraries generated successfully.[/bold green]")

    elif args.command == "servers":
        coordinator = Coordinator(config_path=args.config)
        servers = await coordinator.list_servers()
        table = Table("Available Servers")
        for server in servers:
            table.add_row(server)
        console.print(table)

    elif args.command == "tools":
        coordinator = Coordinator(config_path=args.config)
        try:
            tools = await coordinator.list_tools(args.server)
            table = Table(f"Tools for [bold]{args.server}[/bold]")
            for tool in tools:
                table.add_row(tool)
            console.print(table)
        except (ValueError, RuntimeError) as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

    elif args.command == "skills":
        skills_manager = get_skills_manager()
        skills = skills_manager.list_skills()
        table = Table("Available Skills", "Description", "Tags")
        for name, meta in skills.items():
            table.add_row(name, meta["description"], ", ".join(meta["tags"]))
        console.print(table)

    elif args.command == "search-skills":
        skills_manager = get_skills_manager()
        skills = skills_manager.search_skills(args.query)
        table = Table(f"Search results for [bold]'{args.query}'[/bold]", "Description", "Tags")
        for name, meta in skills.items():
            table.add_row(name, meta["description"], ", ".join(meta["tags"]))
        console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
