"""Pushover notification backend."""

import json
import logging
from typing import Any
from urllib import parse, request

from . import NotifierError

logger = logging.getLogger(__name__)

ENDPOINT = "https://api.pushover.net/1/messages.json"


class PushoverException(NotifierError):
    """Exception for Pushover-specific errors."""

    def __init__(self, *args: Any, response: dict[str, Any] | None = None, **kwargs: Any) -> None:
        """Initialize exception with optional response data.

        Args:
            *args: Positional arguments for Exception
            response: API response data
            **kwargs: Keyword arguments for Exception
        """
        self.response = response
        super().__init__(*args, **kwargs)


class Pushover:
    """Pushover notification backend.

    Sends notifications via the Pushover API service.
    """

    def __init__(
        self,
        api_key: str,
        user_key: str,
        priority: int = 0,
        device: str | None = None,
    ) -> None:
        """Initialize Pushover notifier.

        Args:
            api_key: Pushover application API key
            user_key: User or group key
            priority: Message priority (-2 to 2, default 0)
            device: Optional device name to send to

        Raises:
            ValueError: If api_key or user_key is empty
        """
        if not api_key or not user_key:
            raise ValueError("api_key and user_key are required")

        self._api_key = api_key
        self._user_key = user_key
        self._priority = priority
        self._device = device

    def send(self, msg: str, detail: str = "") -> None:
        """Send a notification via Pushover.

        Args:
            msg: The main message (used as title if detail is provided)
            detail: Optional detailed message body

        Raises:
            PushoverException: If the API request fails
        """
        data: dict[str, str | int] = {
            "token": self._api_key,
            "user": self._user_key,
            "message": msg,
            "priority": self._priority,
        }

        if detail:
            data.update({"title": msg, "message": detail})

        if self._device:
            data["device"] = self._device

        encoded_data = parse.urlencode(data).encode("utf-8")

        req = request.Request(ENDPOINT)
        req.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")

        try:
            with request.urlopen(req, encoded_data) as resp:
                response_data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise PushoverException(f"Failed to send message: {e}") from e

        if response_data.get("status") != 1:
            raise PushoverException("Unable to send message", response=response_data)

        logger.debug(f"Message {response_data.get('request')} sent successfully")
