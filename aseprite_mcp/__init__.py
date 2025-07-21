"""Aseprite MCP - Model Context Protocol implementation for Aseprite.

This package provides a Model Context Protocol (MCP) server that enables
AI assistants to interact with the Aseprite sprite editor through Lua scripting.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

__version__ = "0.2.0"
__author__ = "Divyansh Singh"
__email__ = "divyansh@example.com"
__description__ = "Model Context Protocol server for interacting with Aseprite sprite editor"

mcp = FastMCP("aseprite")

__all__ = ["mcp", "__version__", "__author__", "__email__", "__description__"]