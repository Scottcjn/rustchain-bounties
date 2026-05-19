import logging
import logging.handlers
import os
import sys
from typing import Optional

def setup_logging(log_file: str = "bridge.log", log_level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return the root logger with a file handler and a stream handler.

    The file handler captures detailed log messages (including exception tracebacks)
    at DEBUG level and writes them to a rotating log file. The stream handler outputs
    messages at the specified log level (default INFO) to stdout with a simpler format.

    Args:
        log_file: Path to the log file. Directories are created if missing.
        log_level: Logging level for the stdout handler.

    Returns:
        Configured root logger.

    Raises:
        No exceptions are raised; file handler creation failures are logged to stderr.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers to avoid duplicate output
    logger.handlers.clear()

    # Formatter for file handler: includes full timestamp, level, logger name, message,
    # and automatically appends traceback when exception info is present.
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create the log directory if it does not exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError as e:
            sys.stderr.write(f"Failed to create log directory {log_dir}: {e}\n")
            # Fall through – the RotatingFileHandler will also fail, caught below.

    # File handler with rotation: 10 MB per file, keep 5 backups.
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10_485_760,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except OSError as e:
        sys.stderr.write(f"Failed to create file handler for {log_file}: {e}\n")

    # Stream handler for stdout: simpler format, level controlled by caller.
    stream_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    return logger