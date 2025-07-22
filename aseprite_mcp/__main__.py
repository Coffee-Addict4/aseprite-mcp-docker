"""Main entry point for the Aseprite MCP server."""

import sys
from typing import NoReturn

from . import mcp
from .tools import canvas, drawing, export, file_router  # noqa: F401


def main() -> NoReturn:
    """Main entry point for the application."""
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()