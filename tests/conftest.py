"""Configuration for pytest."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


@pytest.fixture
def mock_aseprite_success():
    """Fixture that mocks successful Aseprite commands."""
    from unittest.mock import patch

    with patch("aseprite_mcp.core.commands.AsepriteCommand.execute_lua_script") as mock_execute, \
         patch("aseprite_mcp.core.commands.AsepriteCommand.run_command") as mock_run:
        mock_execute.return_value = (True, "Success")
        mock_run.return_value = (True, "Success")
        yield {"execute": mock_execute, "run": mock_run}


@pytest.fixture
def mock_aseprite_failure():
    """Fixture that mocks failed Aseprite commands."""
    from unittest.mock import patch

    with patch("aseprite_mcp.core.commands.AsepriteCommand.execute_lua_script") as mock_execute, \
         patch("aseprite_mcp.core.commands.AsepriteCommand.run_command") as mock_run:
        mock_execute.return_value = (False, "Command failed")
        mock_run.return_value = (False, "Command failed")
        yield {"execute": mock_execute, "run": mock_run}
