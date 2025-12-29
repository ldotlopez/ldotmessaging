"""Tests for console notifier."""

import logging
from unittest.mock import patch

from ldotmessaging.console import Console


def test_console_init_default() -> None:
    """Test Console initialization with defaults."""
    console = Console()
    assert console._line_len == 72
    assert console._logger is not None


def test_console_init_custom() -> None:
    """Test Console initialization with custom parameters."""
    console = Console(prog="testapp", line_len=100)
    assert console._line_len == 100
    assert console._logger.name == "testapp"


def test_console_send_simple_message() -> None:
    """Test sending a simple message without detail."""
    console = Console()

    with patch.object(console._logger, "info") as mock_info:
        console.send("Test message")
        mock_info.assert_called_once_with("- Test message")


def test_console_send_with_detail() -> None:
    """Test sending a message with detail text."""
    console = Console(line_len=20)

    with patch.object(console._logger, "info") as mock_info:
        console.send("Title", "This is a long detail message that should wrap")

        # Should be called for title + wrapped detail lines
        assert mock_info.call_count > 1

        # First call should be the title
        first_call = mock_info.call_args_list[0]
        assert first_call[0][0] == "- Title"


def test_console_send_multiline_detail() -> None:
    """Test sending a message with multiline detail."""
    console = Console()

    with patch.object(console._logger, "info") as mock_info:
        console.send("Title", "Line 1\nLine 2\nLine 3")

        # Should be called for title + 3 detail lines
        assert mock_info.call_count == 4


def test_console_logger_level() -> None:
    """Test that logger uses INFO level by default."""
    console = Console()
    assert console._logger.level <= logging.INFO
