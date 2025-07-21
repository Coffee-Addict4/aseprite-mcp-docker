"""Canvas management tools for Aseprite MCP."""

from __future__ import annotations

import logging
from pathlib import Path

from ..core.commands import AsepriteCommand, AsepriteCommandError
from .. import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def create_canvas(
    width: int, height: int, filename: str = "canvas.aseprite"
) -> str:
    """Create a new Aseprite canvas with specified dimensions.

    Args:
        width: Width of the canvas in pixels (must be > 0)
        height: Height of the canvas in pixels (must be > 0)
        filename: Name of the output file (default: canvas.aseprite)

    Returns:
        Status message indicating success or failure
    """
    # Validate input parameters
    if width <= 0 or height <= 0:
        return "Error: Width and height must be positive integers"

    if width > 8192 or height > 8192:
        return "Error: Canvas dimensions too large (max 8192x8192)"

    # Ensure filename has .aseprite extension
    file_path = Path(filename)
    if file_path.suffix.lower() not in [".aseprite", ".ase"]:
        filename = f"{file_path.stem}.aseprite"

    script = f"""
    local spr = Sprite({width}, {height})
    if spr then
        spr:saveAs("{filename}")
        return "Canvas created successfully: {filename}"
    else
        return "Failed to create sprite"
    end
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script)

        if success:
            logger.info(f"Canvas created: {filename} ({width}x{height})")
            return f"Canvas created successfully: {filename} ({width}x{height})"
        else:
            logger.error(f"Failed to create canvas: {output}")
            return f"Failed to create canvas: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def add_layer(filename: str, layer_name: str) -> str:
    """Add a new layer to the Aseprite file.

    Args:
        filename: Name of the Aseprite file to modify
        layer_name: Name of the new layer (must not be empty)

    Returns:
        Status message indicating success or failure
    """
    if not layer_name.strip():
        return "Error: Layer name cannot be empty"

    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    # Escape layer name for Lua
    escaped_name = layer_name.replace('"', '\\"')

    script = f"""
    local spr = app.activeSprite
    if not spr then
        return "Error: No active sprite"
    end

    app.transaction("Add Layer", function()
        local new_layer = spr:newLayer()
        if new_layer then
            new_layer.name = "{escaped_name}"
        else
            return "Error: Failed to create layer"
        end
    end)

    spr:saveAs(spr.filename)
    return "Layer added successfully"
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script, file_path)

        if success:
            logger.info(f"Layer '{layer_name}' added to {filename}")
            return f"Layer '{layer_name}' added successfully to {filename}"
        else:
            logger.error(f"Failed to add layer: {output}")
            return f"Failed to add layer: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def add_frame(filename: str) -> str:
    """Add a new frame to the Aseprite file.

    Args:
        filename: Name of the Aseprite file to modify

    Returns:
        Status message indicating success or failure
    """
    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    script = """
    local spr = app.activeSprite
    if not spr then
        return "Error: No active sprite"
    end

    app.transaction("Add Frame", function()
        local new_frame = spr:newFrame()
        if not new_frame then
            return "Error: Failed to create frame"
        end
    end)

    spr:saveAs(spr.filename)
    return "Frame added successfully"
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script, file_path)

        if success:
            logger.info(f"Frame added to {filename}")
            return f"New frame added successfully to {filename}"
        else:
            logger.error(f"Failed to add frame: {output}")
            return f"Failed to add frame: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def get_canvas_info(filename: str) -> str:
    """Get information about an Aseprite canvas.

    Args:
        filename: Name of the Aseprite file to inspect

    Returns:
        Canvas information including dimensions, layers, and frames
    """
    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    script = """
    local spr = app.activeSprite
    if not spr then
        return "Error: No active sprite"
    end

    local info = {
        width = spr.width,
        height = spr.height,
        layers = #spr.layers,
        frames = #spr.frames,
        colorMode = spr.colorMode
    }

    return "Canvas: " .. info.width .. "x" .. info.height ..
           ", Layers: " .. info.layers ..
           ", Frames: " .. info.frames ..
           ", Color Mode: " .. tostring(info.colorMode)
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script, file_path)

        if success:
            return output
        else:
            return f"Failed to get canvas info: {output}"

    except AsepriteCommandError as e:
        return f"Error executing Aseprite command: {e}"