"""
Logging utility module.
Provides centralized logging configuration for the application.
"""

import logging
import sys
from pathlib import Path


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_file: str = "daily_briefing.log"
) -> logging.Logger:
    """
    Setup and configure a logger instance.

    Args:
        name (str): Logger name (usually __name__ of the calling module)
        level (int): Logging level (default: logging.INFO)
        log_to_file (bool): Whether to log to file in addition to console
        log_file (str): Log file name

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_to_file:
        project_root = Path(__file__).parent.parent
        log_path = project_root / log_file

        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
