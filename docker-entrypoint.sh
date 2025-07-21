#!/bin/bash
set -e

# Aseprite MCP Server Docker Entry Point

echo "Starting Aseprite MCP Server..."
echo "Version: $(python -c 'from aseprite_mcp import __version__; print(__version__)')"
echo "Mode: ${ASEPRITE_MCP_MODE:-mcp}"
echo "Port: ${PORT:-8000}"
echo "Aseprite Path: ${ASEPRITE_PATH:-aseprite}"

# Check if Aseprite is available
if command -v aseprite >/dev/null 2>&1; then
    echo "Aseprite found: $(which aseprite)"
    aseprite --version || echo "Warning: Could not get Aseprite version"
else
    echo "Warning: Aseprite not found in PATH"
fi

# Create necessary directories
mkdir -p /app/projects /app/exports

# Set permissions
chown -R appuser:appuser /app/projects /app/exports

# Execute the main command
exec "$@"
