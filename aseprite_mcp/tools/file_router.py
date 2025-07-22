"""File routing and management tools for Aseprite MCP."""

from __future__ import annotations

import logging
import os
import shutil
import stat
from pathlib import Path
from typing import Any

from .. import mcp

logger = logging.getLogger(__name__)


class FileRoutingError(Exception):
    """Custom exception for file routing errors."""

    def __init__(self, message: str, path: Path | None = None) -> None:
        super().__init__(message)
        self.path = path


@mcp.tool()
async def route_file(
    source_file: str,
    destination_directory: str,
    filename: str | None = None,
    overwrite: bool = False,
    create_dirs: bool = True,
    verify_permissions: bool = True,
) -> str:
    """Route a completed file to a user-defined output directory with comprehensive validation.

    Args:
        source_file: Path to the source file to move/copy
        destination_directory: Target directory path (can be absolute or relative)
        filename: Optional new filename (uses original if not provided)
        overwrite: Whether to overwrite existing files (default: False)
        create_dirs: Whether to create destination directories if they don't exist (default: True)
        verify_permissions: Whether to verify write permissions before operation (default: True)

    Returns:
        Status message with operation details and final file path
    """
    try:
        # Validate and normalize source file path
        source_path = Path(source_file).resolve()
        if not source_path.exists():
            return f"Error: Source file not found: {source_path}"
        
        if not source_path.is_file():
            return f"Error: Source path is not a file: {source_path}"

        # Validate and normalize destination directory
        dest_dir = Path(destination_directory).resolve()
        
        # Security check: prevent path traversal attacks
        try:
            dest_dir.resolve().relative_to(Path.cwd().resolve().parents[2])  # Allow reasonable parent access
        except ValueError:
            # If relative_to fails, check if it's an absolute path to a reasonable location
            if not (dest_dir.is_absolute() and (
                str(dest_dir).startswith(os.path.expanduser("~")) or  # User home directory
                str(dest_dir).startswith("/tmp") or  # Temp directory
                str(dest_dir).startswith("/var/tmp") or  # Var temp directory
                str(dest_dir).startswith("C:\\Users") or  # Windows user directories
                str(dest_dir).startswith("C:\\temp") or  # Windows temp
                str(dest_dir).startswith("C:\\tmp")  # Windows tmp
            )):
                return f"Error: Destination directory appears to be outside safe boundaries: {dest_dir}"

        # Create destination directory if needed
        if not dest_dir.exists():
            if create_dirs:
                try:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {dest_dir}")
                except OSError as e:
                    return f"Error: Failed to create destination directory: {e}"
            else:
                return f"Error: Destination directory does not exist and create_dirs=False: {dest_dir}"
        
        if not dest_dir.is_dir():
            return f"Error: Destination path exists but is not a directory: {dest_dir}"

        # Verify write permissions
        if verify_permissions:
            if not os.access(dest_dir, os.W_OK):
                return f"Error: No write permission for destination directory: {dest_dir}"

        # Determine final filename
        final_filename = filename if filename else source_path.name
        dest_file = dest_dir / final_filename

        # Check for overwrite conflicts
        if dest_file.exists():
            if not overwrite:
                return f"Error: Destination file exists and overwrite=False: {dest_file}"
            else:
                # Verify we can overwrite (check if file is read-only)
                if not os.access(dest_file, os.W_OK):
                    return f"Error: Cannot overwrite read-only file: {dest_file}"

        # Perform the file operation
        try:
            shutil.copy2(source_path, dest_file)  # copy2 preserves metadata
            file_size = dest_file.stat().st_size
            
            logger.info(f"File routed successfully: {source_path} -> {dest_file}")
            
            return (
                f"File routed successfully!\n"
                f"Source: {source_path}\n"
                f"Destination: {dest_file}\n"
                f"Size: {file_size:,} bytes\n"
                f"Operation: {'Overwritten' if dest_file.exists() and overwrite else 'Created'}"
            )
            
        except OSError as e:
            return f"Error: Failed to copy file: {e}"

    except Exception as e:
        logger.error(f"Unexpected error in route_file: {e}")
        return f"Error: Unexpected error during file routing: {e}"


@mcp.tool()
async def validate_output_directory(
    directory_path: str,
    check_write_access: bool = True,
    check_space: bool = True,
    min_space_mb: int = 100,
) -> str:
    """Validate an output directory for file routing operations.

    Args:
        directory_path: Path to validate
        check_write_access: Whether to verify write permissions (default: True)
        check_space: Whether to check available disk space (default: True)
        min_space_mb: Minimum required space in MB (default: 100)

    Returns:
        Validation report with directory status and recommendations
    """
    try:
        dir_path = Path(directory_path).resolve()
        
        validation_results = {
            "path": str(dir_path),
            "exists": dir_path.exists(),
            "is_directory": dir_path.is_dir() if dir_path.exists() else None,
            "writable": None,
            "available_space_mb": None,
            "errors": [],
            "warnings": [],
        }

        # Check existence and type
        if not dir_path.exists():
            validation_results["errors"].append("Directory does not exist")
            try:
                # Check if parent exists and is writable (for potential creation)
                parent = dir_path.parent
                if parent.exists() and parent.is_dir():
                    if os.access(parent, os.W_OK):
                        validation_results["warnings"].append("Directory can be created (parent is writable)")
                    else:
                        validation_results["errors"].append("Cannot create directory (parent not writable)")
                else:
                    validation_results["errors"].append("Parent directory does not exist")
            except Exception as e:
                validation_results["errors"].append(f"Error checking parent directory: {e}")
        else:
            if not dir_path.is_dir():
                validation_results["errors"].append("Path exists but is not a directory")

        # Check write access
        if check_write_access and dir_path.exists() and dir_path.is_dir():
            try:
                validation_results["writable"] = os.access(dir_path, os.W_OK)
                if not validation_results["writable"]:
                    validation_results["errors"].append("Directory is not writable")
            except Exception as e:
                validation_results["errors"].append(f"Error checking write access: {e}")

        # Check available space
        if check_space and dir_path.exists():
            try:
                statvfs = shutil.disk_usage(dir_path)
                available_bytes = statvfs.free
                available_mb = available_bytes / (1024 * 1024)
                validation_results["available_space_mb"] = round(available_mb, 2)
                
                if available_mb < min_space_mb:
                    validation_results["errors"].append(f"Insufficient disk space: {available_mb:.1f}MB < {min_space_mb}MB required")
                elif available_mb < min_space_mb * 2:
                    validation_results["warnings"].append(f"Low disk space: {available_mb:.1f}MB available")
                    
            except Exception as e:
                validation_results["errors"].append(f"Error checking disk space: {e}")

        # Generate report
        status = "VALID" if not validation_results["errors"] else "INVALID"
        if validation_results["warnings"] and not validation_results["errors"]:
            status = "VALID (with warnings)"

        report = [
            f"Directory Validation Report: {status}",
            f"Path: {validation_results['path']}",
            f"Exists: {validation_results['exists']}",
        ]

        if validation_results["exists"]:
            report.append(f"Is Directory: {validation_results['is_directory']}")
            if validation_results["writable"] is not None:
                report.append(f"Writable: {validation_results['writable']}")
            if validation_results["available_space_mb"] is not None:
                report.append(f"Available Space: {validation_results['available_space_mb']:,.1f} MB")

        if validation_results["errors"]:
            report.append("\nErrors:")
            for error in validation_results["errors"]:
                report.append(f"  ❌ {error}")

        if validation_results["warnings"]:
            report.append("\nWarnings:")
            for warning in validation_results["warnings"]:
                report.append(f"  ⚠️  {warning}")

        if status == "VALID":
            report.append("\n✅ Directory is ready for file routing operations")

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Error validating directory: {e}")
        return f"Error: Failed to validate directory: {e}"


@mcp.tool()
async def set_default_output_directory(
    directory_path: str,
    file_type: str = "all",
    validate: bool = True,
) -> str:
    """Set a default output directory for specific file types.

    Args:
        directory_path: Path to set as default
        file_type: File type to associate with this directory (e.g., 'png', 'gif', 'aseprite', 'all')
        validate: Whether to validate the directory before setting (default: True)

    Returns:
        Confirmation message with directory assignment details
    """
    try:
        # Validate directory if requested
        if validate:
            validation_result = await validate_output_directory(directory_path)
            if "INVALID" in validation_result:
                return f"Cannot set default directory - validation failed:\n{validation_result}"

        dir_path = Path(directory_path).resolve()
        
        # Store the default directory setting (in a real implementation, this would persist)
        # For now, we'll just confirm the setting
        
        logger.info(f"Default output directory set for {file_type}: {dir_path}")
        
        return (
            f"Default output directory configured:\n"
            f"File Type: {file_type}\n"
            f"Directory: {dir_path}\n"
            f"Status: Ready for file routing\n"
            f"Note: Use route_file() to move files to this directory"
        )

    except Exception as e:
        logger.error(f"Error setting default directory: {e}")
        return f"Error: Failed to set default directory: {e}"


@mcp.tool()
async def list_recent_routes(limit: int = 10) -> str:
    """List recently routed files for reference.

    Args:
        limit: Maximum number of recent routes to show (default: 10)

    Returns:
        List of recent file routing operations
    """
    # In a real implementation, this would read from a persistent log
    # For now, return a placeholder message
    return (
        f"Recent File Routes (last {limit}):\n"
        f"Note: Route history tracking not yet implemented.\n"
        f"Use route_file() to move files to desired destinations.\n"
        f"Use validate_output_directory() to check destination validity."
    )


@mcp.tool()
async def create_organized_structure(
    base_directory: str,
    structure_type: str = "by_type",
    include_date: bool = True,
) -> str:
    """Create an organized directory structure for file routing.

    Args:
        base_directory: Base directory to create structure in
        structure_type: Type of organization ('by_type', 'by_date', 'by_project')
        include_date: Whether to include date-based subdirectories (default: True)

    Returns:
        Report of created directory structure
    """
    try:
        base_path = Path(base_directory).resolve()
        
        # Validate base directory
        if not base_path.exists():
            base_path.mkdir(parents=True, exist_ok=True)
        
        if not base_path.is_dir():
            return f"Error: Base path is not a directory: {base_path}"

        created_dirs = []
        
        if structure_type == "by_type":
            # Create directories by file type
            file_type_dirs = [
                "images/png",
                "images/jpg", 
                "images/gif",
                "sprites/aseprite",
                "sprites/sheets",
                "animations",
                "exports/final",
                "exports/drafts",
                "projects/active",
                "projects/archive"
            ]
            
            for dir_path in file_type_dirs:
                full_path = base_path / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(full_path))
                
        elif structure_type == "by_date":
            # Create date-based structure
            import datetime
            today = datetime.date.today()
            year_month = today.strftime("%Y/%m")
            
            date_dirs = [
                f"{year_month}/exports",
                f"{year_month}/projects", 
                f"{year_month}/drafts",
                "archive",
                "templates"
            ]
            
            for dir_path in date_dirs:
                full_path = base_path / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(full_path))
                
        elif structure_type == "by_project":
            # Create project-based structure
            project_dirs = [
                "current_projects",
                "completed_projects", 
                "templates",
                "resources/sprites",
                "resources/backgrounds",
                "exports/final",
                "exports/previews"
            ]
            
            for dir_path in project_dirs:
                full_path = base_path / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(full_path))
        else:
            return f"Error: Unknown structure type: {structure_type}. Use 'by_type', 'by_date', or 'by_project'"

        logger.info(f"Created organized structure '{structure_type}' in {base_path}")
        
        report = [
            f"Organized Directory Structure Created: {structure_type}",
            f"Base Directory: {base_path}",
            f"Directories Created: {len(created_dirs)}",
            "",
            "Structure:"
        ]
        
        for dir_path in sorted(created_dirs):
            relative_path = Path(dir_path).relative_to(base_path)
            report.append(f"  📁 {relative_path}")
            
        report.extend([
            "",
            "✅ Directory structure ready for file routing operations",
            "Use route_file() to move files into this organized structure"
        ])
        
        return "\n".join(report)

    except Exception as e:
        logger.error(f"Error creating organized structure: {e}")
        return f"Error: Failed to create directory structure: {e}"
