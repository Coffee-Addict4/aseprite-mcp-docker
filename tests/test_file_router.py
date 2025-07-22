"""Tests for file router functionality."""

from __future__ import annotations

import os
import tempfile

import pytest

from aseprite_mcp.tools.file_router import route_file, validate_output_directory


class TestFileRouter:
    """Test core file routing functionality."""

    @pytest.fixture
    def temp_source_file(self):
        """Create a temporary source file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content")
            temp_file = f.name
        yield temp_file
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.mark.asyncio
    async def test_route_file_basic(self, temp_source_file, temp_dir):
        """Test basic file routing."""
        result = await route_file(
            source_file=temp_source_file,
            destination_directory=temp_dir,
            filename="test.txt"
        )
        
        assert "successfully" in result.lower()

    @pytest.mark.asyncio
    async def test_route_file_nonexistent_source(self, temp_dir):
        """Test routing with nonexistent source file."""
        result = await route_file(
            source_file="/nonexistent/file.txt",
            destination_directory=temp_dir
        )
        
        assert "error" in result.lower()

    @pytest.mark.asyncio
    async def test_validate_directory_valid(self, temp_dir):
        """Test directory validation with valid path."""
        result = await validate_output_directory(temp_dir)
        
        assert "valid" in result.lower() or "accessible" in result.lower()

    @pytest.mark.asyncio
    async def test_validate_directory_invalid(self):
        """Test directory validation with invalid path."""
        result = await validate_output_directory("/nonexistent/path")
        
        assert "error" in result.lower() or "not found" in result.lower()
