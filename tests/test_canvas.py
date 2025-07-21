"""Tests for canvas management tools."""

from __future__ import annotations

import tempfile
from unittest.mock import AsyncMock, patch

import pytest

from aseprite_mcp.core.commands import AsepriteCommandError
from aseprite_mcp.tools.canvas import add_frame, add_layer, create_canvas, get_canvas_info


class TestCanvasTools:
    """Test cases for canvas management tools."""

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.execute_lua_script")
    async def test_create_canvas_success(self, mock_execute: AsyncMock) -> None:
        """Test successful canvas creation."""
        mock_execute.return_value = (True, "Canvas created successfully")

        result = await create_canvas(800, 600, "test.aseprite")

        assert "Canvas created successfully" in result
        assert "800x600" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_canvas_invalid_dimensions(self) -> None:
        """Test canvas creation with invalid dimensions."""
        result = await create_canvas(0, 600, "test.aseprite")
        assert "Error: Width and height must be positive" in result

        result = await create_canvas(800, -100, "test.aseprite")
        assert "Error: Width and height must be positive" in result

    @pytest.mark.asyncio
    async def test_create_canvas_too_large(self) -> None:
        """Test canvas creation with dimensions too large."""
        result = await create_canvas(10000, 600, "test.aseprite")
        assert "Error: Canvas dimensions too large" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.execute_lua_script")
    async def test_create_canvas_command_failure(self, mock_execute: AsyncMock) -> None:
        """Test canvas creation with command failure."""
        mock_execute.return_value = (False, "Command failed")

        result = await create_canvas(800, 600, "test.aseprite")

        assert "Failed to create canvas" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.execute_lua_script")
    async def test_add_layer_success(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful layer addition."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.return_value = (True, "Layer added successfully")

        result = await add_layer("test.aseprite", "new_layer")

        assert "Layer 'new_layer' added successfully" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_layer_empty_name(self) -> None:
        """Test layer addition with empty name."""
        result = await add_layer("test.aseprite", "")
        assert "Error: Layer name cannot be empty" in result

        result = await add_layer("test.aseprite", "   ")
        assert "Error: Layer name cannot be empty" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.validate_file_exists")
    async def test_add_layer_file_not_found(self, mock_validate: AsyncMock) -> None:
        """Test layer addition with non-existing file."""
        mock_validate.side_effect = AsepriteCommandError("File not found")

        result = await add_layer("nonexistent.aseprite", "new_layer")

        assert "File not found" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.execute_lua_script")
    async def test_add_frame_success(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful frame addition."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.return_value = (True, "Frame added successfully")

        result = await add_frame("test.aseprite")

        assert "New frame added successfully" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.execute_lua_script")
    async def test_get_canvas_info_success(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful canvas info retrieval."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.return_value = (True, "Canvas: 800x600, Layers: 2, Frames: 3")

        result = await get_canvas_info("test.aseprite")

        assert "Canvas: 800x600" in result
        assert "Layers: 2" in result
        assert "Frames: 3" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.canvas.AsepriteCommand.execute_lua_script")
    async def test_canvas_command_error_handling(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test error handling for canvas operations."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.side_effect = AsepriteCommandError("Aseprite not found")

        result = await add_layer("test.aseprite", "test_layer")

        assert "Error executing Aseprite command" in result
        assert "Aseprite not found" in result
