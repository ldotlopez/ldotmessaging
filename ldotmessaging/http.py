"""HTTP source for fetching messages."""

import logging
from datetime import datetime, timedelta
from typing import Any
from urllib import request

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) ldotmessaging/1.0"


class Http:
    """HTTP source for fetching content from URLs.

    Supports basic caching to avoid excessive requests.
    """

    def __init__(self, url: str, cache_delta: int = 60) -> None:
        """Initialize HTTP source.

        Args:
            url: URL to fetch from
            cache_delta: Cache duration in seconds (default 60)
        """
        self._url = url
        self._cache_delta = timedelta(seconds=cache_delta)
        self._cached_content: bytes | None = None
        self._cache_time: datetime | None = None

    def recv(self, data: Any = None) -> bytes:
        """Fetch content from the URL.

        Args:
            data: POST data (not currently supported)

        Returns:
            The fetched content as bytes

        Raises:
            NotImplementedError: If POST data is provided
            Exception: If the HTTP request fails
        """
        if data is not None:
            raise NotImplementedError("POST requests are not supported")

        # Check cache
        now = datetime.now()
        if (
            self._cached_content is not None
            and self._cache_time is not None
            and (now - self._cache_time) < self._cache_delta
        ):
            logger.debug(f"Returning cached content for {self._url}")
            return self._cached_content

        # Fetch new content
        logger.debug(f"Fetching {self._url}")
        req = request.Request(self._url, headers={"User-Agent": USER_AGENT})

        try:
            with request.urlopen(req) as response:
                content = response.read()
                self._cached_content = content
                self._cache_time = now
                return content
        except Exception as e:
            logger.error(f"Failed to fetch {self._url}: {e}")
            raise

    def clear_cache(self) -> None:
        """Clear the cached content."""
        self._cached_content = None
        self._cache_time = None
