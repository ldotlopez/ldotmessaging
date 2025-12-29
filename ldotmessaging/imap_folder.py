"""IMAP folder source for reading email messages."""

import email
import imaplib
import logging
import mailbox
import time
from collections.abc import Sequence
from datetime import datetime, timedelta
from email.message import Message
from pathlib import Path

logger = logging.getLogger(__name__)


def email_date_to_datetime(date_str: str) -> datetime:
    """Convert email date string to datetime object.

    Args:
        date_str: Email date string

    Returns:
        Datetime object
    """
    parsed = email.utils.parsedate(date_str)
    if parsed is None:
        return datetime.now()
    timestamp = time.mktime(parsed)
    return datetime.fromtimestamp(timestamp)


def is_email_newer_than(msg: Message, max_age_days: int, now: datetime | None = None) -> bool:
    """Check if email is newer than max_age days.

    Args:
        msg: Email message
        max_age_days: Maximum age in days
        now: Reference time (defaults to current time)

    Returns:
        True if message is newer than max_age days
    """
    if now is None:
        now = datetime.now()

    date_str = msg.get("date", "")
    if not date_str:
        return False

    msg_date = email_date_to_datetime(date_str)
    delta = now - msg_date
    return delta <= timedelta(days=max_age_days)


class ImapFolder:
    """IMAP folder source for reading email messages.

    Supports both IMAP connections and local mbox files.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int = 993,
        username: str | None = None,
        password: str | None = None,
        ssl: bool = True,
        folder: str = "INBOX",
        mbox_paths: str | Sequence[str] | None = None,
        max_age: int = 60,
    ) -> None:
        """Initialize IMAP folder source.

        Args:
            host: IMAP server host (required for IMAP mode)
            port: IMAP server port (default 993)
            username: IMAP username
            password: IMAP password
            ssl: Use SSL/TLS connection
            folder: IMAP folder name (default INBOX)
            mbox_paths: Path(s) to local mbox file(s)
            max_age: Maximum age of messages in days

        Raises:
            ValueError: If neither host nor mbox_paths is provided
        """
        self._max_age = max_age

        if host:
            if not username or not password:
                raise ValueError("Username and password required for IMAP")

            self._mode = "imap"
            self._imap_config = {
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "ssl": ssl,
                "folder": folder,
            }
        elif mbox_paths:
            self._mode = "mbox"
            if isinstance(mbox_paths, str):
                mbox_paths = [mbox_paths]
            self._mbox_paths = [Path(p) for p in mbox_paths]
        else:
            raise ValueError("Either host or mbox_paths must be provided")

    def recv(self, flatten: bool = True) -> list[Message]:
        """Receive messages from the source.

        Args:
            flatten: If True, flatten multipart messages

        Returns:
            List of email messages
        """
        if self._mode == "imap":
            messages = self._recv_imap()
        else:
            messages = self._recv_mbox()

        # Decode message payloads
        self._decode_messages(messages)

        if flatten:
            messages = self._flatten_messages(messages)

        return messages

    def _recv_imap(self) -> list[Message]:
        """Fetch messages from IMAP server."""
        config = self._imap_config
        imap_class = imaplib.IMAP4_SSL if config["ssl"] else imaplib.IMAP4

        with imap_class(config["host"], config["port"]) as mail:
            mail.login(config["username"], config["password"])
            mail.select(config["folder"])

            messages: list[Message] = []
            now = datetime.now()

            # Fetch both seen and unseen messages
            for query, flag_mod, flags in [
                ("(SEEN)", None, None),
                ("(UNSEEN)", "-FLAGS", r"\SEEN"),
            ]:
                typ, data = mail.search(None, query)
                if typ != "OK":
                    continue

                uids = sorted((int(uid) for uid in data[0].split()), reverse=True)

                for uid in uids:
                    uid_bytes = str(uid).encode("ascii")
                    resp, data = mail.fetch(uid_bytes, "(RFC822)")

                    if resp != "OK":
                        continue

                    msg = email.message_from_bytes(data[0][1])

                    if flag_mod:
                        mail.store(uid_bytes, flag_mod, flags)

                    if is_email_newer_than(msg, self._max_age, now):
                        messages.append(msg)
                    else:
                        break

            return sorted(
                messages, key=lambda m: email_date_to_datetime(m.get("date", "")), reverse=True
            )

    def _recv_mbox(self) -> list[Message]:
        """Fetch messages from mbox files."""
        messages: list[Message] = []

        for mbox_path in self._mbox_paths:
            if not mbox_path.exists():
                logger.warning(f"Mbox file not found: {mbox_path}")
                continue

            mbox = mailbox.mbox(str(mbox_path))
            messages.extend(mbox.values())

        now = datetime.now()
        return [m for m in messages if is_email_newer_than(m, self._max_age, now)]

    def _decode_messages(self, messages: list[Message]) -> None:
        """Decode message payloads to text."""
        for message in messages:
            for part in message.walk():
                payload_bytes = part.get_payload(decode=True)

                if payload_bytes is None:
                    continue

                # Try multiple encodings
                encodings = ["utf-8", "iso-8859-15", "ascii"]
                charset = part.get_content_charset()
                if charset:
                    encodings = [charset.split(",")[0]] + encodings

                for encoding in encodings:
                    try:
                        payload_text = payload_bytes.decode(encoding)
                        part.set_payload(payload_text, charset=encoding)
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue
                else:
                    logger.warning("Unable to decode message part")

    def _flatten_messages(self, messages: list[Message]) -> list[Message]:
        """Flatten multipart messages into single parts.

        Args:
            messages: List of messages to flatten

        Returns:
            List of flattened message parts
        """
        # Copy headers from parent to children
        for message in messages:
            parent_keys = set(message.keys())
            for part in message.walk():
                part_keys = set(part.keys())
                for key in parent_keys - part_keys:
                    part[key] = message[key]

        # Extract non-multipart parts
        return [part for message in messages for part in message.walk() if not part.is_multipart()]
