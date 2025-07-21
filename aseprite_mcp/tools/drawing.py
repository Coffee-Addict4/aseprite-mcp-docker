"""Drawing tools for Aseprite MCP."""

from __future__ import annotations

import logging
import re
from typing import Any

from ..core.commands import AsepriteCommand, AsepriteCommandError
from .. import mcp

logger = logging.getLogger(__name__)


def validate_hex_color(color: str) -> tuple[bool, str]:
    """Validate and normalize a hex color string.

    Args:
        color: Hex color string (e.g., "#FF0000" or "FF0000")

    Returns:
        tuple: (is_valid, normalized_color)
    """
    # Remove # if present and convert to uppercase
    color = color.lstrip("#").upper()

    # Validate hex format
    if not re.match(r"^[0-9A-F]{6}$", color):
        return False, color

    return True, color


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB values.

    Args:
        color: Hex color string without #

    Returns:
        tuple: (r, g, b) values
    """
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return r, g, b


@mcp.tool()
async def draw_pixels(filename: str, pixels: list[dict[str, Any]]) -> str:
    """Draw pixels on the canvas with specified colors.

    Args:
        filename: Name of the Aseprite file to modify
        pixels: List of pixel data, each containing:
            {"x": int, "y": int, "color": str}
            where color is a hex code like "#FF0000"

    Returns:
        Status message indicating success or failure
    """
    if not pixels:
        return "Error: No pixels provided"

    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    # Validate pixel data
    for i, pixel in enumerate(pixels):
        if not isinstance(pixel, dict):
            return f"Error: Pixel {i} is not a dictionary"

        required_keys = ["x", "y", "color"]
        for key in required_keys:
            if key not in pixel:
                return f"Error: Pixel {i} missing required key '{key}'"

        # Validate coordinates
        if not isinstance(pixel["x"], int) or not isinstance(pixel["y"], int):
            return f"Error: Pixel {i} coordinates must be integers"

        if pixel["x"] < 0 or pixel["y"] < 0:
            return f"Error: Pixel {i} coordinates must be non-negative"

        # Validate color
        is_valid, _ = validate_hex_color(pixel["color"])
        if not is_valid:
            return f"Error: Pixel {i} has invalid color format '{pixel['color']}'"

    script = """
    local spr = app.activeSprite
    if not spr then
        return "Error: No active sprite"
    end

    app.transaction("Draw Pixels", function()
        local cel = app.activeCel
        if not cel then
            -- Create a new cel if none exists
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = spr:newCel(app.activeLayer, app.activeFrame)
            if not cel then
                return "Error: Could not create cel"
            end
        end

        local img = cel.image
    """

    # Add pixel drawing commands
    for pixel in pixels:
        x = pixel["x"]
        y = pixel["y"]
        is_valid, normalized_color = validate_hex_color(pixel["color"])
        if is_valid:
            r, g, b = hex_to_rgb(normalized_color)
            script += f"""
        if {x} >= 0 and {y} >= 0 and {x} < img.width and {y} < img.height then
            img:putPixel({x}, {y}, Color({r}, {g}, {b}, 255))
        end
        """

    script += """
    end)

    spr:saveAs(spr.filename)
    return "Pixels drawn successfully"
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script, file_path)

        if success:
            logger.info(f"Drew {len(pixels)} pixels in {filename}")
            return f"Successfully drew {len(pixels)} pixels in {filename}"
        else:
            logger.error(f"Failed to draw pixels: {output}")
            return f"Failed to draw pixels: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def draw_line(
    filename: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: str = "#000000",
    thickness: int = 1,
) -> str:
    """Draw a line on the canvas.

    Args:
        filename: Name of the Aseprite file to modify
        x1: Starting x coordinate
        y1: Starting y coordinate
        x2: Ending x coordinate
        y2: Ending y coordinate
        color: Hex color code (default: "#000000")
        thickness: Line thickness in pixels (default: 1, max: 100)

    Returns:
        Status message indicating success or failure
    """
    # Validate input parameters
    if thickness < 1 or thickness > 100:
        return "Error: Thickness must be between 1 and 100"

    is_valid, normalized_color = validate_hex_color(color)
    if not is_valid:
        return f"Error: Invalid color format '{color}'"

    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    r, g, b = hex_to_rgb(normalized_color)

    script = f"""
    local spr = app.activeSprite
    if not spr then
        return "Error: No active sprite"
    end

    app.transaction("Draw Line", function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = spr:newCel(app.activeLayer, app.activeFrame)
            if not cel then
                return "Error: Could not create cel"
            end
        end

        local color = Color({r}, {g}, {b}, 255)
        local brush = Brush()
        brush.size = {thickness}

        app.useTool({{
            tool="line",
            color=color,
            brush=brush,
            points={{Point({x1}, {y1}), Point({x2}, {y2})}}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Line drawn successfully"
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script, file_path)

        if success:
            logger.info(f"Drew line from ({x1},{y1}) to ({x2},{y2}) in {filename}")
            return f"Line drawn successfully from ({x1},{y1}) to ({x2},{y2}) in {filename}"
        else:
            logger.error(f"Failed to draw line: {output}")
            return f"Failed to draw line: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def draw_rectangle(
    filename: str,
    x: int,
    y: int,
    width: int,
    height: int,
    color: str = "#000000",
    fill: bool = False,
) -> str:
    """Draw a rectangle on the canvas.

    Args:
        filename: Name of the Aseprite file to modify
        x: Top-left x coordinate
        y: Top-left y coordinate
        width: Width of the rectangle (must be > 0)
        height: Height of the rectangle (must be > 0)
        color: Hex color code (default: "#000000")
        fill: Whether to fill the rectangle (default: False)

    Returns:
        Status message indicating success or failure
    """
    # Validate input parameters
    if width <= 0 or height <= 0:
        return "Error: Width and height must be positive"

    is_valid, normalized_color = validate_hex_color(color)
    if not is_valid:
        return f"Error: Invalid color format '{color}'"

    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    r, g, b = hex_to_rgb(normalized_color)
    tool = "filled_rectangle" if fill else "rectangle"

    script = f"""
    local spr = app.activeSprite
    if not spr then
        return "Error: No active sprite"
    end

    app.transaction("Draw Rectangle", function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = spr:newCel(app.activeLayer, app.activeFrame)
            if not cel then
                return "Error: Could not create cel"
            end
        end

        local color = Color({r}, {g}, {b}, 255)
        app.useTool({{
            tool="{tool}",
            color=color,
            points={{Point({x}, {y}), Point({x + width}, {y + height})}}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Rectangle drawn successfully"
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script, file_path)

        fill_text = "filled " if fill else ""
        if success:
            logger.info(f"Drew {fill_text}rectangle at ({x},{y}) size {width}x{height} in {filename}")
            return f"{fill_text.title()}Rectangle drawn successfully at ({x},{y}) size {width}x{height} in {filename}"
        else:
            logger.error(f"Failed to draw rectangle: {output}")
            return f"Failed to draw rectangle: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def fill_area(filename: str, x: int, y: int, color: str = "#000000") -> str:
    """Fill an area with color using the paint bucket tool.

    Args:
        filename: Name of the Aseprite file to modify
        x: X coordinate to fill from
        y: Y coordinate to fill from
        color: Hex color code (default: "#000000")

    Returns:
        Status message indicating success or failure
    """
    is_valid, normalized_color = validate_hex_color(color)
    if not is_valid:
        return f"Error: Invalid color format '{color}'"

    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    r, g, b = hex_to_rgb(normalized_color)

    script = f"""
    local spr = app.activeSprite
    if not spr then
        return "Error: No active sprite"
    end

    app.transaction("Fill Area", function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = spr:newCel(app.activeLayer, app.activeFrame)
            if not cel then
                return "Error: Could not create cel"
            end
        end

        local color = Color({r}, {g}, {b}, 255)
        app.useTool({{
            tool="paint_bucket",
            color=color,
            points={{Point({x}, {y})}}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Area filled successfully"
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script, file_path)

        if success:
            logger.info(f"Filled area at ({x},{y}) in {filename}")
            return f"Area filled successfully at ({x},{y}) in {filename}"
        else:
            logger.error(f"Failed to fill area: {output}")
            return f"Failed to fill area: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def draw_circle(
    filename: str,
    center_x: int,
    center_y: int,
    radius: int,
    color: str = "#000000",
    fill: bool = False,
) -> str:
    """Draw a circle on the canvas.

    Args:
        filename: Name of the Aseprite file to modify
        center_x: X coordinate of circle center
        center_y: Y coordinate of circle center
        radius: Radius of the circle in pixels (must be > 0)
        color: Hex color code (default: "#000000")
        fill: Whether to fill the circle (default: False)

    Returns:
        Status message indicating success or failure
    """
    if radius <= 0:
        return "Error: Radius must be positive"

    is_valid, normalized_color = validate_hex_color(color)
    if not is_valid:
        return f"Error: Invalid color format '{color}'"

    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    r, g, b = hex_to_rgb(normalized_color)
    tool = "filled_ellipse" if fill else "ellipse"

    script = f"""
    local spr = app.activeSprite
    if not spr then
        return "Error: No active sprite"
    end

    app.transaction("Draw Circle", function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = spr:newCel(app.activeLayer, app.activeFrame)
            if not cel then
                return "Error: Could not create cel"
            end
        end

        local color = Color({r}, {g}, {b}, 255)
        app.useTool({{
            tool="{tool}",
            color=color,
            points={{
                Point({center_x - radius}, {center_y - radius}),
                Point({center_x + radius}, {center_y + radius})
            }}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Circle drawn successfully"
    """

    try:
        success, output = AsepriteCommand.execute_lua_script(script, file_path)

        fill_text = "filled " if fill else ""
        if success:
            logger.info(f"Drew {fill_text}circle at ({center_x},{center_y}) radius {radius} in {filename}")
            return f"{fill_text.title()}Circle drawn successfully at ({center_x},{center_y}) radius {radius} in {filename}"
        else:
            logger.error(f"Failed to draw circle: {output}")
            return f"Failed to draw circle: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"
    