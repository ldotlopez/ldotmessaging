"""Command-line interface for ldotmessaging."""

import argparse
import configparser
import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import Any, NoReturn

logger = logging.getLogger(__name__)


def load_backend_class(backend_name: str) -> type:
    """Load a backend class by name.

    Args:
        backend_name: Name of the backend (e.g., 'pushover', 'console')

    Returns:
        The backend class

    Raises:
        ImportError: If backend cannot be loaded
    """
    try:
        module = importlib.import_module(f"ldotmessaging.{backend_name}")
    except ImportError as e:
        raise ImportError(f"Failed to import backend '{backend_name}': {e}") from e

    # Convert snake_case to PascalCase
    class_name = "".join(word.capitalize() for word in backend_name.split("_"))

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            f"Backend module '{backend_name}' does not have class '{class_name}'"
        ) from e


def filter_kwargs_by_signature(func: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Filter kwargs to only include parameters accepted by func.

    Args:
        func: Function or class to inspect
        kwargs: Dictionary of keyword arguments

    Returns:
        Filtered dictionary containing only valid parameters
    """
    sig = inspect.signature(func)
    valid_params = set(sig.parameters.keys())
    return {k: v for k, v in kwargs.items() if k in valid_params}


def main() -> NoReturn:
    """Main CLI entry point."""
    # Parse initial arguments
    parser = argparse.ArgumentParser(
        description="Messaging microframework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-b",
        "--backend",
        required=True,
        help="Backend to use (e.g., pushover, console, twitter)",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="Configuration file path",
    )
    parser.add_argument(
        "--init-section",
        default="init",
        help="Config section for initialization parameters (default: init)",
    )
    parser.add_argument(
        "--send-section",
        default="send",
        help="Config section for send parameters (default: send)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    # Parse known args to get backend and config file
    args, remaining = parser.parse_known_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load config file if provided
    init_opts: dict[str, Any] = {}
    send_opts: dict[str, Any] = {}

    if args.config:
        if not args.config.exists():
            logger.error(f"Config file not found: {args.config}")
            sys.exit(1)

        config = configparser.ConfigParser()
        config.read(args.config)

        if args.init_section in config:
            init_opts.update(dict(config[args.init_section]))

        if args.send_section in config:
            send_opts.update(dict(config[args.send_section]))

    # Parse remaining arguments for backend-specific options
    if remaining:
        # Build parser for backend options
        backend_parser = argparse.ArgumentParser()

        # Find all --flag=value or --flag patterns
        i = 0
        while i < len(remaining):
            arg = remaining[i]
            if arg.startswith("--"):
                arg_name = arg.split("=")[0][2:].replace("-", "_")
                backend_parser.add_argument(f"--{arg_name.replace('_', '-')}", dest=arg_name)
            i += 1

        backend_parser.add_argument("message", nargs="+", help="Message to send")

        try:
            backend_args = backend_parser.parse_args(remaining)
        except SystemExit:
            logger.error("Failed to parse arguments")
            sys.exit(1)

        # Separate init and send options
        for key, value in vars(backend_args).items():
            if value is None:
                continue
            if key.startswith("init_"):
                init_opts[key[5:]] = value
            elif key != "message":
                send_opts[key] = value

        message = " ".join(backend_args.message)
    else:
        logger.error("No message provided")
        sys.exit(1)

    # Load backend
    try:
        backend_class = load_backend_class(args.backend)
    except ImportError as e:
        logger.error(str(e))
        sys.exit(1)

    # Filter options to match backend signatures
    filtered_init_opts = filter_kwargs_by_signature(backend_class, init_opts)
    filtered_send_opts = filter_kwargs_by_signature(backend_class.send, send_opts)

    # Initialize backend and send message
    try:
        backend = backend_class(**filtered_init_opts)
        backend.send(message, **filtered_send_opts)
        logger.info("Message sent successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
