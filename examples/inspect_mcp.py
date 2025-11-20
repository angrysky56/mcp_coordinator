import inspect

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

print("StdioServerParameters signature:")
print(inspect.signature(StdioServerParameters))

print("\nstdio_client signature:")
print(inspect.signature(stdio_client))
