import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(
    name: str,
    log_file: str = None,
    level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
    console: bool = True,
) -> logging.Logger:
    """
    Setup and return a logger instance.

    Args:
        name (str): Logger name.
        log_file (str): Optional path to log file.
        level (int): Logging level (e.g. logging.INFO).
        max_bytes (int): Max file size before rotating.
        backup_count (int): Number of rotated log files to keep.
        console (bool): If True, logs also output to console.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent double logging if root logger is configured

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Prevent duplicate handlers
    existing_handlers = {type(h) for h in logger.handlers}

    # Console handler
    if console and logging.StreamHandler not in existing_handlers:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    # File handler
    if log_file and RotatingFileHandler not in existing_handlers:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # logger.info("Logger initialized.")  # Optional
    return logger
