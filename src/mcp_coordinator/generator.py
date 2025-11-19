"""
Python code generator for MCP tool wrappers.

Creates importable Python modules from discovered MCP server capabilities.
Implements Anthropic's "filesystem-based progressive disclosure" pattern.
"""

import json
from pathlib import Path
from typing import Any


class ToolGenerator:
    """Generates Python wrapper code for MCP tools."""

    def __init__(self, output_dir: str | Path = "./mcp_tools") -> None:
        """
        Initialize generator.

        Args:
            output_dir: Where to write generated Python files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_tool_function(
        self,
        tool_name: str,
        tool_schema: dict[str, Any],
        server_name: str,
    ) -> str:
        """
        Generate Python function code for a single tool.

        Args:
            tool_name: Name of the tool
            tool_schema: Tool schema from discovery
            server_name: Parent server name

        Returns:
            Python function definition as string
        """
        description = tool_schema.get("description", "No description available")
        input_schema = tool_schema.get("input_schema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])

        # Generate function signature
        params = []
        for param_name, param_info in properties.items():
            param_type = self._python_type_from_json_schema(param_info)
            is_required = param_name in required

            if is_required:
                params.append(f"{param_name}: {param_type}")
            else:
                default = "None"
                params.append(f"{param_name}: {param_type} | None = {default}")

        params_str = ", ".join(params)

        # Generate docstring
        docstring_lines = [f'    """{description}']

        if properties:
            docstring_lines.append("")
            docstring_lines.append("    Args:")
            for param_name, param_info in properties.items():
                param_desc = param_info.get("description", "")
                docstring_lines.append(f"        {param_name}: {param_desc}")

        docstring_lines.append("")
        docstring_lines.append("    Returns:")
        docstring_lines.append("        Tool execution result")
        docstring_lines.append('    """')
        docstring = "\n".join(docstring_lines)

        # Generate function body
        function_code = f'''
async def {tool_name}({params_str}) -> Any:
{docstring}
    from mcp_coordinator.runtime import call_mcp_tool

    # Build parameters dict, excluding None values
    params = {{}}
'''

        for param_name in properties.keys():
            function_code += f'''    if {param_name} is not None:
        params["{param_name}"] = {param_name}
'''

        function_code += f'''
    return await call_mcp_tool(
        server_name="{server_name}",
        tool_name="{tool_name}",
        arguments=params,
    )
'''

        return function_code

    def _python_type_from_json_schema(self, schema: dict[str, Any]) -> str:
        """
        Convert JSON schema type to Python type hint.

        Args:
            schema: JSON schema object

        Returns:
            Python type string
        """
        schema_type = schema.get("type", "any")

        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": "list",
            "object": "dict",
            "null": "None",
        }

        if schema_type in type_map:
            base_type = type_map[schema_type]

            # Handle arrays with item types
            if schema_type == "array" and "items" in schema:
                item_type = self._python_type_from_json_schema(schema["items"])
                return f"list[{item_type}]"

            # Handle objects with additional properties
            if schema_type == "object":
                return "dict[str, Any]"

            return base_type

        return "Any"

    def generate_server_module(
        self,
        server_name: str,
        server_info: dict[str, Any],
    ) -> None:
        """
        Generate Python module for an entire server.

        Creates a file like mcp_tools/chroma.py with all tools.

        Args:
            server_name: Name of the server
            server_info: Server capabilities from discovery
        """
        module_path = self.output_dir / f"{server_name}.py"

        # Start with module docstring and imports
        module_code = f'''"""
Auto-generated wrapper for {server_name} MCP server.

This module provides Python function wrappers for all tools
exposed by the {server_name} server.

DO NOT EDIT MANUALLY - regenerate using mcp-coordinator generator.
"""

from typing import Any

'''

        # Generate function for each tool
        tools = server_info.get("tools", {})

        if not tools:
            module_code += f'''
# No tools found for {server_name}
'''
        else:
            for tool_name, tool_schema in tools.items():
                tool_func = self.generate_tool_function(
                    tool_name,
                    tool_schema,
                    server_name,
                )
                module_code += tool_func + "\n"

            # Generate list_tools helper
            tool_names = list(tools.keys())
            module_code += f'''

def list_tools() -> list[str]:
    """Get list of all available tools in this server."""
    return {tool_names!r}
'''

        # Write to file
        module_path.write_text(module_code)

    def generate_index_module(self, server_names: list[str]) -> None:
        """
        Generate mcp_tools/__init__.py for server discovery.

        Args:
            server_names: List of server names
        """
        init_path = self.output_dir / "__init__.py"

        init_code = '''"""
MCP Tools - Auto-generated importable wrappers for MCP servers.

This package is automatically generated by mcp-coordinator.
DO NOT EDIT MANUALLY.

Usage:
    from mcp_tools import list_servers
    from mcp_tools.chroma import query, add_documents
"""

def list_servers() -> list[str]:
    """Get list of all available MCP servers."""
'''

        init_code += f"    return {server_names!r}\n"

        init_path.write_text(init_code)

    def generate_readme(self) -> None:
        """Generate README for mcp_tools directory."""
        readme_path = self.output_dir / "README.md"

        readme_content = """# MCP Tools (Auto-Generated)

This directory contains auto-generated Python wrappers for your MCP servers.

**⚠️ DO NOT EDIT FILES IN THIS DIRECTORY MANUALLY**

Files here are generated by `mcp-coordinator` based on your MCP server configuration.

## Regenerating

To regenerate these files (e.g., after adding/updating servers):

```python
from mcp_coordinator import Coordinator

coordinator = Coordinator("~/.config/claude/mcp_servers.json")
await coordinator.generate_tools()
```

## Usage

```python
# Discover available servers
from mcp_tools import list_servers
print(list_servers())

# Import specific server tools
from mcp_tools.chroma import query, add_documents

# Use tools in your code
results = await query(collection="papers", query_text="transformers")
```

## Structure

Each server gets its own module:
- `mcp_tools/chroma.py` - Tools from the chroma server
- `mcp_tools/arxiv.py` - Tools from the arxiv server
- etc.

Each module provides:
- Individual tool functions with full type hints
- `list_tools()` function to see what's available
"""

        readme_path.write_text(readme_content)

    def generate_all(self, servers_info: dict[str, dict[str, Any]]) -> None:
        """
        Generate complete mcp_tools package.

        Args:
            servers_info: Dictionary of server capabilities from discovery
        """
        server_names = []

        # Generate module for each server
        for server_name, server_info in servers_info.items():
            if "error" in server_info:
                print(f"Skipping {server_name}: {server_info['error']}")
                continue

            self.generate_server_module(server_name, server_info)
            server_names.append(server_name)

        # Generate package index
        self.generate_index_module(server_names)

        # Generate README
        self.generate_readme()

        print(f"Generated {len(server_names)} server modules in {self.output_dir}")


def generate_from_config(
    config_path: str | Path,
    output_dir: str | Path = "./mcp_tools",
) -> None:
    """
    High-level function to generate tools from config.

    Args:
        config_path: Path to MCP server configuration
        output_dir: Where to generate Python modules
    """
    import asyncio

    from mcp_coordinator.discovery import discover_all_servers

    # Discover all servers
    print(f"Discovering servers from {config_path}...")
    servers_info = asyncio.run(discover_all_servers(config_path))

    # Generate Python wrappers
    print("Generating Python wrappers...")
    generator = ToolGenerator(output_dir)
    generator.generate_all(servers_info)

    print("✓ Generation complete!")
