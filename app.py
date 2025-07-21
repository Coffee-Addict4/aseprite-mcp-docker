#!/usr/bin/env python3
"""
Aseprite MCP Server - Simplified Entry Point

This module serves as the main entry point for the Aseprite MCP server.
Focuses on core MCP functionality following modularity principles.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

from aseprite_mcp import mcp

# Configure minimal logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce logging verbosity
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for MCP server."""
    try:
        # Simple MCP server - no web interface
        await mcp.run()
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server")
        sys.exit(0)
    except Exception as e:
        logger.error(f"MCP server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check environment
    mode = os.getenv("ASEPRITE_MCP_MODE", "mcp")
    if mode != "mcp":
        logger.warning("Only MCP mode supported. Defaulting to MCP.")
    
    # Run MCP server
    asyncio.run(main())
