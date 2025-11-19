import inspect
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

print("StdioServerParameters signature:")
print(inspect.signature(StdioServerParameters))

print("\nstdio_client signature:")
print(inspect.signature(stdio_client))
