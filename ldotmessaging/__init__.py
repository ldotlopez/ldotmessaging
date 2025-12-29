"""Modern messaging microframework for Python 3.11+."""

from typing import Any, Protocol

__version__ = "1.0.0"
__all__ = ["Notifier", "Source", "NotifierError", "NotifierRegistry"]


class Notifier(Protocol):
    """Protocol for notification backends."""

    def send(self, msg: str, detail: str = "") -> None:
        """Send a notification message.

        Args:
            msg: The main message text
            detail: Optional detailed message

        Raises:
            NotifierError: If sending fails
        """
        ...


class Source(Protocol):
    """Protocol for message sources."""

    def recv(self) -> Any:
        """Receive messages from the source.

        Returns:
            Received messages in implementation-specific format
        """
        ...


class NotifierError(Exception):
    """Exception raised when notification sending fails."""

    pass


class NotifierRegistry:
    """Registry for managing multiple notifiers."""

    def __init__(self) -> None:
        self._notifiers: dict[str, Notifier] = {}

    def register(self, name: str, notifier: Notifier) -> None:
        """Register a notifier with a name.

        Args:
            name: Unique identifier for the notifier
            notifier: The notifier instance
        """
        self._notifiers[name] = notifier

    def unregister(self, name: str) -> None:
        """Remove a notifier from the registry.

        Args:
            name: Identifier of the notifier to remove

        Raises:
            KeyError: If notifier doesn't exist
        """
        del self._notifiers[name]

    def send_all(self, msg: str, detail: str = "") -> None:
        """Send message to all registered notifiers.

        Args:
            msg: The main message text
            detail: Optional detailed message
        """
        for notifier in self._notifiers.values():
            notifier.send(msg, detail)

    def get(self, name: str) -> Notifier | None:
        """Get a notifier by name.

        Args:
            name: Notifier identifier

        Returns:
            The notifier instance or None if not found
        """
        return self._notifiers.get(name)


# Global registry instance for convenience
_registry = NotifierRegistry()


def enable(name: str, notifier: Notifier) -> None:
    """Enable a notifier in the global registry.

    Args:
        name: Unique identifier for the notifier
        notifier: The notifier instance
    """
    _registry.register(name, notifier)


def disable(name: str) -> None:
    """Disable a notifier in the global registry.

    Args:
        name: Identifier of the notifier to remove
    """
    _registry.unregister(name)


def send(msg: str, detail: str = "") -> None:
    """Send message to all enabled notifiers.

    Args:
        msg: The main message text
        detail: Optional detailed message
    """
    _registry.send_all(msg, detail)
