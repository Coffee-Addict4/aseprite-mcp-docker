"""Tests for export tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from aseprite_mcp.core.commands import AsepriteCommandError
from aseprite_mcp.tools.export import export_animation, export_sprite, export_spritesheet


class TestExportTools:
    """Test cases for export tools."""

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.export.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.export.AsepriteCommand.run_command")
    async def test_export_sprite_success(
        self, mock_run: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful sprite export."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_run.return_value = (True, "Export successful")

        result = await export_sprite("test.aseprite", "output.png", "png")

        assert "Sprite exported successfully" in result
        assert "PNG image" in result
        mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_sprite_unsupported_format(self) -> None:
        """Test sprite export with unsupported format."""
        result = await export_sprite("test.aseprite", "output.xyz", "xyz")
        assert "Error: Unsupported format" in result
        assert "Supported formats:" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.export.AsepriteCommand.validate_file_exists")
    async def test_export_sprite_file_not_found(self, mock_validate: AsyncMock) -> None:
        """Test sprite export with non-existing file."""
        mock_validate.side_effect = AsepriteCommandError("File not found")

        result = await export_sprite("nonexistent.aseprite", "output.png")
        assert "File not found" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.export.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.export.AsepriteCommand.run_command")
    async def test_export_sprite_command_failure(
        self, mock_run: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test sprite export with command failure."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_run.return_value = (False, "Export failed")

        result = await export_sprite("test.aseprite", "output.png")

        assert "Failed to export sprite" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.export.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.export.AsepriteCommand.run_command")
    async def test_export_animation_success(
        self, mock_run: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful animation export."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_run.return_value = (True, "Animation exported")

        result = await export_animation("test.aseprite", "anim.gif", "gif", 2)

        assert "Animation exported successfully" in result
        assert "scale: 2x" in result
        mock_run.assert_called_once()

        # Check that scale was included in command
        call_args = mock_run.call_args[0][0]
        assert "--scale" in call_args
        assert "2" in call_args

    @pytest.mark.asyncio
    async def test_export_animation_invalid_format(self) -> None:
        """Test animation export with invalid format."""
        result = await export_animation("test.aseprite", "anim.png", "png")
        assert "Error: Animation export only supports 'gif' and 'webp' formats" in result

    @pytest.mark.asyncio
    async def test_export_animation_invalid_scale(self) -> None:
        """Test animation export with invalid scale."""
        result = await export_animation("test.aseprite", "anim.gif", "gif", 0)
        assert "Error: Scale must be between 1 and 10" in result

        result = await export_animation("test.aseprite", "anim.gif", "gif", 11)
        assert "Error: Scale must be between 1 and 10" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.export.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.export.AsepriteCommand.run_command")
    async def test_export_spritesheet_success(
        self, mock_run: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful sprite sheet export."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_run.return_value = (True, "Sprite sheet exported")

        result = await export_spritesheet("test.aseprite", "sheet.png", "png", "horizontal")

        assert "Sprite sheet exported successfully" in result
        assert "horizontal layout" in result
        mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_spritesheet_invalid_format(self) -> None:
        """Test sprite sheet export with invalid format."""
        result = await export_spritesheet("test.aseprite", "sheet.gif", "gif")
        assert "Error: Sprite sheet export supports: png, jpg, jpeg, bmp, tga" in result

    @pytest.mark.asyncio
    async def test_export_spritesheet_invalid_type(self) -> None:
        """Test sprite sheet export with invalid sheet type."""
        result = await export_spritesheet("test.aseprite", "sheet.png", "png", "invalid")
        assert "Error: Invalid sheet type" in result
        assert "Valid types:" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.export.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.export.AsepriteCommand.run_command")
    async def test_export_command_error_handling(
        self, mock_run: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test error handling for export operations."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_run.side_effect = AsepriteCommandError("Command failed")

        result = await export_sprite("test.aseprite", "output.png")

        assert "Error executing Aseprite command" in result
        assert "Command failed" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.export.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.export.AsepriteCommand.run_command")
    async def test_export_filename_extension_handling(
        self, mock_run: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test that file extensions are handled correctly."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_run.return_value = (True, "Export successful")

        # Test with filename without extension
        await export_sprite("test.aseprite", "output", "png")

        # Check that the command was called with .png extension
        call_args = mock_run.call_args[0][0]
        assert "output.png" in call_args
