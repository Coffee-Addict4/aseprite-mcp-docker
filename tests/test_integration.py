"""Integration tests for Aseprite MCP."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from aseprite_mcp.tools.canvas import create_canvas
from aseprite_mcp.tools.drawing import draw_line
from aseprite_mcp.tools.export import export_sprite


class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @patch("aseprite_mcp.core.commands.AsepriteCommand.execute_lua_script")
    @patch("aseprite_mcp.core.commands.AsepriteCommand.run_command")
    async def test_complete_workflow(self, mock_run: object, mock_execute: object) -> None:
        """Test a complete workflow from canvas creation to export."""
        # Mock successful operations
        mock_execute.return_value = (True, "Success")
        mock_run.return_value = (True, "Export successful")

        # Create a temporary directory for test files
        with tempfile.TemporaryDirectory() as tmp_dir:
            canvas_file = Path(tmp_dir) / "test_canvas.aseprite"
            output_file = Path(tmp_dir) / "output.png"

            # Step 1: Create canvas
            result = await create_canvas(800, 600, str(canvas_file))
            assert "Canvas created successfully" in result

            # Step 2: Draw on canvas (this would normally require the file to exist)
            with patch("aseprite_mcp.core.commands.AsepriteCommand.validate_file_exists") as mock_validate:
                mock_validate.return_value = canvas_file
                result = await draw_line(str(canvas_file), 0, 0, 100, 100, "#FF0000")
                assert "Line drawn successfully" in result

            # Step 3: Export canvas
            with patch("aseprite_mcp.core.commands.AsepriteCommand.validate_file_exists") as mock_validate:
                mock_validate.return_value = canvas_file
                result = await export_sprite(str(canvas_file), str(output_file), "png")
                assert "Sprite exported successfully" in result

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_error_propagation(self) -> None:
        """Test that errors are properly propagated through the system."""
        # Test with non-existent file - should fail gracefully
        result = await draw_line("nonexistent.aseprite", 0, 0, 100, 100)
        assert "Error" in result or "not found" in result

    @pytest.mark.asyncio
    async def test_parameter_validation_chain(self) -> None:
        """Test parameter validation across multiple operations."""
        # Test invalid canvas dimensions
        result = await create_canvas(-1, 600)
        assert "Error" in result

        # Test invalid color format
        with patch("aseprite_mcp.core.commands.AsepriteCommand.validate_file_exists") as mock_validate:
            mock_validate.return_value = "/path/to/file.aseprite"
            result = await draw_line("test.aseprite", 0, 0, 100, 100, "invalid_color")
            assert "Error: Invalid color format" in result
