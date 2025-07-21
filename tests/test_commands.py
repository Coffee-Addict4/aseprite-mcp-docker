"""Tests for core Aseprite command functionality."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from aseprite_mcp.core.commands import AsepriteCommand, AsepriteCommandError


class TestAsepriteCommand:
    """Test cases for AsepriteCommand class."""

    def test_get_aseprite_path_default(self) -> None:
        """Test getting default Aseprite path."""
        with patch.dict(os.environ, {}, clear=True):
            path = AsepriteCommand.get_aseprite_path()
            assert path == "aseprite"

    def test_get_aseprite_path_from_env(self) -> None:
        """Test getting Aseprite path from environment variable."""
        test_path = "/usr/local/bin/aseprite"
        with patch.dict(os.environ, {"ASEPRITE_PATH": test_path}):
            path = AsepriteCommand.get_aseprite_path()
            assert path == test_path

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run: Mock) -> None:
        """Test successful command execution."""
        mock_run.return_value.stdout = "success output"
        mock_run.return_value.returncode = 0

        success, output = AsepriteCommand.run_command(["--version"])

        assert success is True
        assert output == "success output"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run: Mock) -> None:
        """Test failed command execution."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, ["aseprite"], stderr="error message")

        success, output = AsepriteCommand.run_command(["--invalid"])

        assert success is False
        assert output == "error message"

    @patch("subprocess.run")
    def test_run_command_timeout(self, mock_run: Mock) -> None:
        """Test command timeout."""
        from subprocess import TimeoutExpired

        mock_run.side_effect = TimeoutExpired(["aseprite"], 30)

        with pytest.raises(AsepriteCommandError, match="timed out"):
            AsepriteCommand.run_command(["--hang"], timeout=30)

    @patch("subprocess.run")
    def test_run_command_file_not_found(self, mock_run: Mock) -> None:
        """Test command with missing executable."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(AsepriteCommandError, match="executable not found"):
            AsepriteCommand.run_command(["--version"])

    @patch.object(AsepriteCommand, "run_command")
    def test_execute_lua_script_success(self, mock_run: Mock) -> None:
        """Test successful Lua script execution."""
        mock_run.return_value = (True, "script output")

        script = "print('hello')"
        success, output = AsepriteCommand.execute_lua_script(script)

        assert success is True
        assert output == "script output"
        mock_run.assert_called_once()

    def test_execute_lua_script_empty(self) -> None:
        """Test empty script content."""
        with pytest.raises(AsepriteCommandError, match="cannot be empty"):
            AsepriteCommand.execute_lua_script("")

    @patch.object(AsepriteCommand, "run_command")
    def test_execute_lua_script_with_file(self, mock_run: Mock) -> None:
        """Test Lua script execution with file."""
        mock_run.return_value = (True, "script output")

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".aseprite", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            script = "print('hello')"
            success, output = AsepriteCommand.execute_lua_script(script, tmp_path)

            assert success is True
            assert output == "script output"
            mock_run.assert_called_once()

            # Check that the file path was included in the arguments
            call_args = mock_run.call_args[0][0]
            assert tmp_path in call_args

        finally:
            os.unlink(tmp_path)

    def test_validate_file_exists_success(self) -> None:
        """Test file validation with existing file."""
        with tempfile.NamedTemporaryFile() as tmp:
            result = AsepriteCommand.validate_file_exists(tmp.name)
            assert isinstance(result, Path)
            assert result.exists()

    def test_validate_file_exists_failure(self) -> None:
        """Test file validation with non-existing file."""
        with pytest.raises(AsepriteCommandError, match="File not found"):
            AsepriteCommand.validate_file_exists("/nonexistent/file.aseprite")
