"""Twitter notification backend."""

import logging
from typing import Any

try:
    import twitter as twapi
except ImportError:
    twapi = None  # type: ignore

from . import NotifierError

logger = logging.getLogger(__name__)


class Twitter:
    """Twitter notification backend.

    Posts status updates to Twitter/X.
    Note: Requires python-twitter package to be installed.
    """

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token: str,
        access_token_secret: str,
    ) -> None:
        """Initialize Twitter notifier.

        Args:
            consumer_key: Twitter API consumer key
            consumer_secret: Twitter API consumer secret
            access_token: Twitter API access token
            access_token_secret: Twitter API access token secret

        Raises:
            ImportError: If python-twitter is not installed
            ValueError: If any credential is empty
        """
        if twapi is None:
            raise ImportError(
                "python-twitter package is required for Twitter notifications. "
                "Install it with: pip install python-twitter"
            )

        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError("All Twitter credentials are required")

        self._api = twapi.Api(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token,
            access_token_secret=access_token_secret,
        )

    def send(self, msg: str, detail: str = "") -> None:
        """Post a status update to Twitter.

        Args:
            msg: The tweet text (detail is ignored)
            detail: Ignored for Twitter backend

        Raises:
            NotifierError: If posting fails
        """
        try:
            self._api.PostUpdate(msg)
            logger.debug(f"Tweet posted: {msg[:50]}...")
        except Exception as e:
            error_msg = f"Failed to post tweet: {e}"
            logger.error(error_msg)

            # Extract error details if available
            if hasattr(e, "response_data") and isinstance(e.response_data, dict):
                errors = e.response_data.get("errors", [])
                for error in errors:
                    logger.error(f"Error {error.get('code')}: {error.get('message')}")
                raise NotifierError(errors) from e

            raise NotifierError(error_msg) from e

    def recv(self, user_name: str | None = None, since: Any = None) -> list[Any]:
        """Receive tweets (not implemented).

        Args:
            user_name: Username to fetch tweets from
            since: Starting point for fetching tweets

        Returns:
            Empty list (not implemented)
        """
        logger.warning("recv() method is not implemented for Twitter backend")
        return []
