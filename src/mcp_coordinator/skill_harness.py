"""
Skill execution harness.

Allows executing skills from the database via CLI, similar to the mcp-code-execution-enhanced pattern.
Usage: python -m mcp_coordinator.skill_harness <skill_name> [args...]
"""

import asyncio
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from mcp_coordinator.skills import get_skills_manager
from mcp_coordinator.coordinator_client import cleanup_global_client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("skill_harness")


async def execute_skill(skill_name: str, kwargs: dict[str, Any]) -> Any:
    """Execute a skill by name with arguments."""
    # Get skill code
    manager = get_skills_manager()
    skill = manager.get_skill(skill_name)

    if skill:
        # DB path
        # Ensure the file exists on disk
        manager.get_import_statement(skill_name)
        module_name = f"skills.{skill_name}"
        function_name = skill["function_name"]
    else:
        # File fallback path
        # Check if skills/{skill_name}.py exists
        skill_file = Path("skills") / f"{skill_name}.py"
        if not skill_file.exists():
            raise ValueError(f"Skill '{skill_name}' not found in DB or skills/ directory")

        logger.info(f"Skill found in file: {skill_file}")
        module_name = f"skills.{skill_name}"
        # We guess the function name is the same as the skill name or 'main' or try to find it?
        # For research.py, the function is 'research_topic'.
        # This is tricky. We might need to inspect the file.
        # Let's assume the function name matches the skill name (common convention) OR 'research_topic' for research.
        # Or we can inspect the module after import.
        function_name = None

    # Import the module
    try:
        # Ensure current directory is in path
        if str(Path.cwd()) not in sys.path:
            sys.path.insert(0, str(Path.cwd()))

        module = __import__(module_name, fromlist=["*"])

        if not function_name:
            # Try to find the function in the module
            # Strategy: look for function with same name as skill, or 'main', or the only exported function
            if hasattr(module, skill_name):
                function_name = skill_name
            elif hasattr(module, "main"):
                function_name = "main"
            elif hasattr(module, "research_topic") and skill_name == "research":
                function_name = "research_topic"
            else:
                # Fallback: find first function that is not private
                import inspect

                funcs = [n for n, o in inspect.getmembers(module, inspect.isfunction) if not n.startswith("_") and o.__module__ == module.__name__]
                if len(funcs) == 1:
                    function_name = funcs[0]
                else:
                    raise ValueError(f"Could not determine entry point function for skill '{skill_name}'")

        func = getattr(module, function_name)
        logger.info(f"Executing function: {function_name}")

        # Execute
        if asyncio.iscoroutinefunction(func):
            result = await func(**kwargs)
        else:
            result = func(**kwargs)

        return result

    except ImportError as e:
        raise RuntimeError(f"Failed to import skill {skill_name}: {e}")
    except Exception as e:
        raise RuntimeError(f"Skill execution failed: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Execute an MCP skill")
    parser.add_argument("skill_name", help="Name of the skill to execute")
    parser.add_argument("--args", help="JSON string of arguments", default="{}")
    # Allow arbitrary arguments as well
    parser.add_argument("extra_args", nargs="*", help="Key=value arguments")

    args = parser.parse_args()

    # Parse arguments
    kwargs = {}
    if args.args:
        try:
            kwargs = json.loads(args.args)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in --args: {args.args}")
            sys.exit(1)

    # Parse extra args (key=value)
    for arg in args.extra_args:
        if "=" in arg:
            k, v = arg.split("=", 1)
            # Try to parse value as JSON/int/float
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                pass  # Keep as string
            kwargs[k] = v

    logger.info(f"Executing skill '{args.skill_name}' with args: {kwargs}")

    try:
        result = await execute_skill(args.skill_name, kwargs)
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        # Cleanup global client if it was used by the skill
        cleanup_global_client()


if __name__ == "__main__":
    asyncio.run(main())
