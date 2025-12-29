"""Console notifier for logging messages."""

import logging
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class Console:
    """Console notifier that outputs messages to a logger."""

    def __init__(self, prog: str | None = None, line_len: int = 72) -> None:
        """Initialize console notifier.

        Args:
            prog: Program name for the logger (defaults to script name)
            line_len: Maximum line length for wrapping detail text
        """
        if prog is None:
            prog = Path(sys.argv[0]).stem if sys.argv else "ldotmessaging"
        self._logger = get_logger(prog)
        self._line_len = line_len

    def send(self, msg: str, detail: str = "") -> None:
        """Send a message to the console.

        Args:
            msg: The main message text
            detail: Optional detailed message that will be wrapped
        """
        self._logger.info(f"- {msg}")

        if detail:
            for line in detail.split("\n"):
                # Wrap long lines
                chunks = [line[i : i + self._line_len] for i in range(0, len(line), self._line_len)]
                for chunk in chunks:
                    self._logger.info(f"  {chunk}")
