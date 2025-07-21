"""Core command functionality for executing Aseprite operations."""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import dotenv

# Load environment variables
dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class AsepriteCommandError(Exception):
    """Custom exception for Aseprite command errors."""

    def __init__(self, message: str, command: list[str] | None = None) -> None:
        super().__init__(message)
        self.command = command


class AsepriteCommand:
    """Helper class for running Aseprite commands with improved error handling."""

    @staticmethod
    def get_aseprite_path() -> str:
        """Get the Aseprite executable path from environment or default."""
        path = os.getenv("ASEPRITE_PATH", "aseprite")
        logger.debug(f"Using Aseprite path: {path}")
        return path

    @staticmethod
    def run_command(args: list[str], timeout: int = 30) -> tuple[bool, str]:
        """Run an Aseprite command with proper error handling.

        Args:
            args: List of command arguments
            timeout: Command timeout in seconds

        Returns:
            tuple: (success, output) where success is a boolean and output is the command output

        Raises:
            AsepriteCommandError: If the command fails or times out
        """
        cmd = [AsepriteCommand.get_aseprite_path()] + args
        logger.info(f"Executing command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
            )
            logger.debug(f"Command succeeded with output: {result.stdout}")
            return True, result.stdout

        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with return code {e.returncode}: {e.stderr}"
            logger.error(error_msg)
            return False, e.stderr

        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout} seconds"
            logger.error(error_msg)
            raise AsepriteCommandError(error_msg, cmd) from e

        except FileNotFoundError as e:
            error_msg = f"Aseprite executable not found: {cmd[0]}"
            logger.error(error_msg)
            raise AsepriteCommandError(error_msg, cmd) from e

        except Exception as e:
            error_msg = f"Unexpected error running command: {e}"
            logger.error(error_msg)
            raise AsepriteCommandError(error_msg, cmd) from e

    @staticmethod
    def execute_lua_script(
        script_content: str,
        filename: str | Path | None = None,
        timeout: int = 30,
    ) -> tuple[bool, str]:
        """Execute a Lua script in Aseprite.

        Args:
            script_content: Lua script code to execute
            filename: Optional filename to open before executing script
            timeout: Script execution timeout in seconds

        Returns:
            tuple: (success, output)

        Raises:
            AsepriteCommandError: If script execution fails
        """
        if not script_content.strip():
            raise AsepriteCommandError("Script content cannot be empty")

        # Create a temporary file for the script
        with tempfile.NamedTemporaryFile(
            suffix=".lua", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(script_content)
            script_path = tmp.name

        try:
            args = ["--batch"]

            # Add filename if provided and exists
            if filename:
                file_path = Path(filename)
                if file_path.exists():
                    args.append(str(file_path))
                    logger.debug(f"Opening file: {file_path}")
                else:
                    logger.warning(f"File not found: {file_path}")

            args.extend(["--script", script_path])

            success, output = AsepriteCommand.run_command(args, timeout=timeout)
            return success, output

        finally:
            # Clean up the temporary script file
            try:
                os.remove(script_path)
                logger.debug(f"Cleaned up temporary script: {script_path}")
            except OSError as e:
                logger.warning(f"Failed to clean up temporary script {script_path}: {e}")

    @staticmethod
    def validate_file_exists(filename: str | Path) -> Path:
        """Validate that a file exists and return its Path object.

        Args:
            filename: Path to the file to validate

        Returns:
            Path object of the validated file

        Raises:
            AsepriteCommandError: If the file doesn't exist
        """
        file_path = Path(filename)
        if not file_path.exists():
            raise AsepriteCommandError(f"File not found: {file_path}")
        return file_path