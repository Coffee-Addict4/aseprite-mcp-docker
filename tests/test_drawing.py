"""Tests for drawing tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from aseprite_mcp.core.commands import AsepriteCommandError
from aseprite_mcp.tools.drawing import (
    draw_circle,
    draw_line,
    draw_pixels,
    draw_rectangle,
    fill_area,
    hex_to_rgb,
    validate_hex_color,
)


class TestDrawingHelpers:
    """Test cases for drawing helper functions."""

    def test_validate_hex_color_valid(self) -> None:
        """Test hex color validation with valid colors."""
        assert validate_hex_color("#FF0000") == (True, "FF0000")
        assert validate_hex_color("ff0000") == (True, "FF0000")
        assert validate_hex_color("123ABC") == (True, "123ABC")

    def test_validate_hex_color_invalid(self) -> None:
        """Test hex color validation with invalid colors."""
        assert validate_hex_color("FF00")[0] is False  # Too short
        assert validate_hex_color("FF00000")[0] is False  # Too long
        assert validate_hex_color("GGHHII")[0] is False  # Invalid characters
        assert validate_hex_color("red")[0] is False  # Not hex

    def test_hex_to_rgb(self) -> None:
        """Test hex to RGB conversion."""
        assert hex_to_rgb("FF0000") == (255, 0, 0)
        assert hex_to_rgb("00FF00") == (0, 255, 0)
        assert hex_to_rgb("0000FF") == (0, 0, 255)
        assert hex_to_rgb("FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("000000") == (0, 0, 0)


class TestDrawingTools:
    """Test cases for drawing tools."""

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.execute_lua_script")
    async def test_draw_pixels_success(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful pixel drawing."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.return_value = (True, "Pixels drawn successfully")

        pixels = [
            {"x": 10, "y": 20, "color": "#FF0000"},
            {"x": 30, "y": 40, "color": "#00FF00"},
        ]

        result = await draw_pixels("test.aseprite", pixels)

        assert "Successfully drew 2 pixels" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_draw_pixels_empty_list(self) -> None:
        """Test pixel drawing with empty list."""
        result = await draw_pixels("test.aseprite", [])
        assert "Error: No pixels provided" in result

    @pytest.mark.asyncio
    async def test_draw_pixels_invalid_data(self) -> None:
        """Test pixel drawing with invalid pixel data."""
        # Invalid pixel data structure
        result = await draw_pixels("test.aseprite", ["invalid"])
        assert "Pixel 0 is not a dictionary" in result

        # Missing required keys
        result = await draw_pixels("test.aseprite", [{"x": 10}])
        assert "missing required key" in result

        # Invalid coordinates
        result = await draw_pixels("test.aseprite", [{"x": -1, "y": 0, "color": "#FF0000"}])
        assert "coordinates must be non-negative" in result

        # Invalid color
        result = await draw_pixels("test.aseprite", [{"x": 0, "y": 0, "color": "invalid"}])
        assert "invalid color format" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.execute_lua_script")
    async def test_draw_line_success(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful line drawing."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.return_value = (True, "Line drawn successfully")

        result = await draw_line("test.aseprite", 0, 0, 100, 100, "#FF0000", 2)

        assert "Line drawn successfully" in result
        assert "from (0,0) to (100,100)" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_draw_line_invalid_thickness(self) -> None:
        """Test line drawing with invalid thickness."""
        result = await draw_line("test.aseprite", 0, 0, 100, 100, "#FF0000", 0)
        assert "Error: Thickness must be between 1 and 100" in result

        result = await draw_line("test.aseprite", 0, 0, 100, 100, "#FF0000", 101)
        assert "Error: Thickness must be between 1 and 100" in result

    @pytest.mark.asyncio
    async def test_draw_line_invalid_color(self) -> None:
        """Test line drawing with invalid color."""
        result = await draw_line("test.aseprite", 0, 0, 100, 100, "invalid")
        assert "Error: Invalid color format" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.execute_lua_script")
    async def test_draw_rectangle_success(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful rectangle drawing."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.return_value = (True, "Rectangle drawn successfully")

        result = await draw_rectangle("test.aseprite", 10, 20, 100, 50, "#0000FF", True)

        assert "Filled Rectangle drawn successfully" in result
        assert "at (10,20) size 100x50" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_draw_rectangle_invalid_dimensions(self) -> None:
        """Test rectangle drawing with invalid dimensions."""
        result = await draw_rectangle("test.aseprite", 0, 0, 0, 100)
        assert "Error: Width and height must be positive" in result

        result = await draw_rectangle("test.aseprite", 0, 0, 100, -50)
        assert "Error: Width and height must be positive" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.execute_lua_script")
    async def test_fill_area_success(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful area filling."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.return_value = (True, "Area filled successfully")

        result = await fill_area("test.aseprite", 50, 75, "#FFFF00")

        assert "Area filled successfully" in result
        assert "at (50,75)" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.execute_lua_script")
    async def test_draw_circle_success(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test successful circle drawing."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.return_value = (True, "Circle drawn successfully")

        result = await draw_circle("test.aseprite", 100, 100, 50, "#FF00FF", False)

        assert "Circle drawn successfully" in result
        assert "at (100,100) radius 50" in result
        mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_draw_circle_invalid_radius(self) -> None:
        """Test circle drawing with invalid radius."""
        result = await draw_circle("test.aseprite", 100, 100, 0)
        assert "Error: Radius must be positive" in result

        result = await draw_circle("test.aseprite", 100, 100, -10)
        assert "Error: Radius must be positive" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.validate_file_exists")
    async def test_drawing_file_not_found(self, mock_validate: AsyncMock) -> None:
        """Test drawing tools with non-existing file."""
        mock_validate.side_effect = AsepriteCommandError("File not found")

        result = await draw_line("nonexistent.aseprite", 0, 0, 100, 100)
        assert "File not found" in result

    @pytest.mark.asyncio
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.validate_file_exists")
    @patch("aseprite_mcp.tools.drawing.AsepriteCommand.execute_lua_script")
    async def test_drawing_command_error(
        self, mock_execute: AsyncMock, mock_validate: AsyncMock
    ) -> None:
        """Test drawing tools with command execution error."""
        mock_validate.return_value = "/path/to/file.aseprite"
        mock_execute.side_effect = AsepriteCommandError("Command failed")

        result = await draw_line("test.aseprite", 0, 0, 100, 100)
        assert "Error executing Aseprite command" in result
