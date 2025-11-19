"""
Helper script for executing code in an isolated environment.

This script is called by SecureExecutor to run code inside a new
network namespace.
"""

import base64
import sys

from smolagents import LocalPythonExecutor


def main():
    """Main entry point for the helper script."""
    if len(sys.argv) != 2:
        print("Usage: python _executor_helper.py <base64_encoded_code>", file=sys.stderr)
        sys.exit(1)

    encoded_code = sys.argv[1]
    try:
        decoded_code = base64.b64decode(encoded_code).decode("utf-8")
        executor = LocalPythonExecutor(additional_authorized_imports=[])
        result = executor.execute(decoded_code)
        print(result)
    except Exception as e:
        print(f"Error executing code: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
