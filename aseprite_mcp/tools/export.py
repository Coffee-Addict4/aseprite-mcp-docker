"""Export tools for Aseprite MCP."""

from __future__ import annotations

import logging
from pathlib import Path

from ..core.commands import AsepriteCommand, AsepriteCommandError
from .. import mcp

logger = logging.getLogger(__name__)

# Supported export formats
SUPPORTED_FORMATS = {
    "png": "PNG image",
    "gif": "GIF animation",
    "jpg": "JPEG image",
    "jpeg": "JPEG image",
    "bmp": "Bitmap image",
    "tga": "Targa image",
    "webp": "WebP image",
}


@mcp.tool()
async def export_sprite(
    filename: str, output_filename: str, format: str = "png"
) -> str:
    """Export the Aseprite file to another format.

    Args:
        filename: Name of the Aseprite file to export
        output_filename: Name of the output file
        format: Output format (default: "png")
               Supported: png, gif, jpg/jpeg, bmp, tga, webp

    Returns:
        Status message indicating success or failure
    """
    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    # Validate and normalize format
    format = format.lower().strip()
    if format not in SUPPORTED_FORMATS:
        supported = ", ".join(SUPPORTED_FORMATS.keys())
        return f"Error: Unsupported format '{format}'. Supported formats: {supported}"

    # Ensure output filename has the correct extension
    output_path = Path(output_filename)
    if output_path.suffix.lower() != f".{format}":
        output_filename = f"{output_path.stem}.{format}"

    # Use batch mode for export
    args = ["--batch", str(file_path), "--save-as", output_filename]

    try:
        success, output = AsepriteCommand.run_command(args)

        if success:
            logger.info(f"Exported {filename} to {output_filename} as {format.upper()}")
            return f"Sprite exported successfully from {filename} to {output_filename} ({SUPPORTED_FORMATS[format]})"
        else:
            logger.error(f"Failed to export sprite: {output}")
            return f"Failed to export sprite: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def export_animation(
    filename: str,
    output_filename: str,
    format: str = "gif",
    scale: int = 1,
) -> str:
    """Export the Aseprite file as an animation.

    Args:
        filename: Name of the Aseprite file to export
        output_filename: Name of the output file
        format: Output format (default: "gif", supports: gif, webp)
        scale: Scale factor for the output (default: 1, max: 10)

    Returns:
        Status message indicating success or failure
    """
    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    # Validate format for animations
    format = format.lower().strip()
    if format not in ["gif", "webp"]:
        return "Error: Animation export only supports 'gif' and 'webp' formats"

    # Validate scale
    if scale < 1 or scale > 10:
        return "Error: Scale must be between 1 and 10"

    # Ensure output filename has the correct extension
    output_path = Path(output_filename)
    if output_path.suffix.lower() != f".{format}":
        output_filename = f"{output_path.stem}.{format}"

    # Build export arguments
    args = ["--batch", str(file_path)]

    if scale > 1:
        args.extend(["--scale", str(scale)])

    args.extend(["--save-as", output_filename])

    try:
        success, output = AsepriteCommand.run_command(args)

        if success:
            logger.info(f"Exported animation {filename} to {output_filename} as {format.upper()}")
            return f"Animation exported successfully from {filename} to {output_filename} (scale: {scale}x)"
        else:
            logger.error(f"Failed to export animation: {output}")
            return f"Failed to export animation: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"


@mcp.tool()
async def export_spritesheet(
    filename: str,
    output_filename: str,
    format: str = "png",
    sheet_type: str = "horizontal",
) -> str:
    """Export the Aseprite file as a sprite sheet.

    Args:
        filename: Name of the Aseprite file to export
        output_filename: Name of the output file
        format: Output format (default: "png")
        sheet_type: Type of sprite sheet layout
                   ("horizontal", "vertical", "rows", "columns", "packed")

    Returns:
        Status message indicating success or failure
    """
    try:
        file_path = AsepriteCommand.validate_file_exists(filename)
    except AsepriteCommandError as e:
        return str(e)

    # Validate format
    format = format.lower().strip()
    if format not in ["png", "jpg", "jpeg", "bmp", "tga"]:
        return "Error: Sprite sheet export supports: png, jpg, jpeg, bmp, tga"

    # Validate sheet type
    valid_types = ["horizontal", "vertical", "rows", "columns", "packed"]
    if sheet_type not in valid_types:
        return f"Error: Invalid sheet type. Valid types: {', '.join(valid_types)}"

    # Ensure output filename has the correct extension
    output_path = Path(output_filename)
    if output_path.suffix.lower() != f".{format}":
        output_filename = f"{output_path.stem}.{format}"

    # Build arguments based on sheet type
    args = ["--batch", str(file_path)]

    if sheet_type == "horizontal":
        args.extend(["--sheet-type", "horizontal"])
    elif sheet_type == "vertical":
        args.extend(["--sheet-type", "vertical"])
    elif sheet_type == "rows":
        args.extend(["--sheet-type", "rows"])
    elif sheet_type == "columns":
        args.extend(["--sheet-type", "columns"])
    elif sheet_type == "packed":
        args.extend(["--sheet-type", "packed"])

    args.extend(["--save-as", output_filename])

    try:
        success, output = AsepriteCommand.run_command(args)

        if success:
            logger.info(f"Exported sprite sheet {filename} to {output_filename}")
            return f"Sprite sheet exported successfully from {filename} to {output_filename} ({sheet_type} layout)"
        else:
            logger.error(f"Failed to export sprite sheet: {output}")
            return f"Failed to export sprite sheet: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"