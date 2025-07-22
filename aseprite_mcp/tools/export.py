"""Export tools for Aseprite MCP."""

from __future__ import annotations

import logging
import os
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


def get_downloads_dir() -> Path:
    """Get the Downloads directory path and ensure it exists."""
    downloads_dir = Path("/app/downloads")
    downloads_dir.mkdir(exist_ok=True)
    return downloads_dir


def prepare_output_path(output_filename: str, format: str) -> str:
    """Prepare the full output path in the Downloads directory with correct extension.
    
    Args:
        output_filename: Base filename (can be just name or include path)
        format: File format extension
        
    Returns:
        Full path to the output file in Downloads directory
    """
    downloads_dir = get_downloads_dir()
    
    # Extract just the filename if a path was provided
    output_path = Path(output_filename)
    filename = output_path.name
    
    # Ensure correct extension
    if not filename.lower().endswith(f".{format}"):
        filename = f"{output_path.stem}.{format}"
    
    # Return full path in Downloads directory
    return str(downloads_dir / filename)


@mcp.tool()
async def export_sprite(
    filename: str, output_filename: str, format: str = "png"
) -> str:
    """Export the Aseprite file to another format.
    Exported files are automatically placed in the Downloads folder.

    Args:
        filename: Name of the Aseprite file to export
        output_filename: Name of the output file (will be placed in Downloads)
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

    # Prepare output path in Downloads directory
    output_path = prepare_output_path(output_filename, format)

    # Use batch mode for export
    args = ["--batch", str(file_path), "--save-as", output_path]

    try:
        success, output = AsepriteCommand.run_command(args)

        if success:
            logger.info(f"Exported {filename} to {output_path} as {format.upper()}")
            return f"Sprite exported successfully from {filename} to Downloads/{Path(output_path).name} ({SUPPORTED_FORMATS[format]})"
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
    Exported files are automatically placed in the Downloads folder.

    Args:
        filename: Name of the Aseprite file to export
        output_filename: Name of the output file (will be placed in Downloads)
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

    # Prepare output path in Downloads directory
    output_path = prepare_output_path(output_filename, format)

    # Build export arguments
    args = ["--batch", str(file_path)]

    if scale > 1:
        args.extend(["--scale", str(scale)])

    args.extend(["--save-as", output_path])

    try:
        success, output = AsepriteCommand.run_command(args)

        if success:
            logger.info(f"Exported animation {filename} to {output_path} as {format.upper()}")
            return f"Animation exported successfully from {filename} to Downloads/{Path(output_path).name} (scale: {scale}x)"
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
    Exported files are automatically placed in the Downloads folder.

    Args:
        filename: Name of the Aseprite file to export
        output_filename: Name of the output file (will be placed in Downloads)
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

    # Prepare output path in Downloads directory
    output_path = prepare_output_path(output_filename, format)

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

    args.extend(["--save-as", output_path])

    try:
        success, output = AsepriteCommand.run_command(args)

        if success:
            logger.info(f"Exported sprite sheet {filename} to {output_path}")
            return f"Sprite sheet exported successfully from {filename} to Downloads/{Path(output_path).name} ({sheet_type} layout)"
        else:
            logger.error(f"Failed to export sprite sheet: {output}")
            return f"Failed to export sprite sheet: {output}"

    except AsepriteCommandError as e:
        logger.error(f"Aseprite command error: {e}")
        return f"Error executing Aseprite command: {e}"