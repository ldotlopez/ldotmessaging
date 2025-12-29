# ldotmessaging

A modern Python messaging microframework for sending notifications across multiple backends.

## Features

- **Multiple Backends**: Support for Pushover, Twitter, Console, HTTP, and IMAP
- **Type-Safe**: Full type hints for Python 3.11+
- **Modern Python**: Uses latest Python features and best practices
- **Extensible**: Easy to add custom notifiers
- **CLI Support**: Command-line interface for quick notifications

## Installation

```bash
pip install ldotmessaging
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Using as a Library

```python
from ldotmessaging import enable, send
from ldotmessaging.console import Console
from ldotmessaging.pushover import Pushover

# Enable notifiers
enable("console", Console())
enable("pushover", Pushover(
    api_key="your-api-key",
    user_key="your-user-key"
))

# Send to all enabled notifiers
send("Hello World!", "This is a detailed message")
```

### Using Individual Notifiers

```python
from ldotmessaging.pushover import Pushover

notifier = Pushover(
    api_key="your-api-key",
    user_key="your-user-key",
    priority=1
)

notifier.send("Important Alert", "Something happened!")
```

### Using the CLI

```bash
# Simple console output
ldotmessaging -b console "Hello World"

# With config file
ldotmessaging -b pushover -c config.ini "Alert message"

# With inline options
ldotmessaging -b pushover --init-api-key=KEY --init-user-key=USER "Message"
```

## Backends

### Console

Outputs messages to the console via Python logging.

```python
from ldotmessaging.console import Console

console = Console(prog="myapp", line_len=80)
console.send("Status update", "Detailed information here")
```

### Pushover

Sends notifications via [Pushover](https://pushover.net/).

```python
from ldotmessaging.pushover import Pushover

pushover = Pushover(
    api_key="your-api-key",
    user_key="your-user-key",
    priority=0,  # -2 to 2
    device="iphone"  # optional
)
pushover.send("Title", "Message body")
```

### Twitter

Posts status updates to Twitter/X.

```python
from ldotmessaging.twitter import Twitter

twitter = Twitter(
    consumer_key="...",
    consumer_secret="...",
    access_token="...",
    access_token_secret="..."
)
twitter.send("Tweet text")
```

### HTTP Source

Fetches content from URLs with caching.

```python
from ldotmessaging.http import Http

source = Http("https://api.example.com/status", cache_delta=300)
content = source.recv()
```

### IMAP Folder

Reads email messages from IMAP servers or mbox files.

```python
from ldotmessaging.imap_folder import ImapFolder

# IMAP mode
imap = ImapFolder(
    host="imap.gmail.com",
    username="user@example.com",
    password="password",
    folder="INBOX",
    max_age=7  # days
)
messages = imap.recv(flatten=True)

# Mbox mode
mbox = ImapFolder(
    mbox_paths=["/path/to/mail.mbox"],
    max_age=30
)
messages = mbox.recv()
```

## Configuration File

Create a `config.ini` file:

```ini
[init]
api_key = your-pushover-api-key
user_key = your-pushover-user-key
priority = 1

[send]
# Send-specific options here
```

Then use it:

```bash
ldotmessaging -b pushover -c config.ini "Your message"
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/ldotlopez/ldotmessaging
cd ldotmessaging

# Install in development mode
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type check
mypy src/

# Run tests
pytest
```

## License

GNU General Public License v2.0 or later (GPLv2+)

## Author

Luis López (ldotlopez@gmail.com)

## Links

- [GitHub Repository](https://github.com/ldotlopez/ldotmessaging)
- [Issue Tracker](https://github.com/ldotlopez/ldotmessaging/issues)
