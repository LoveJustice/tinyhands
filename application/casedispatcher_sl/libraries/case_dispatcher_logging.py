import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(
    name, file_name, level=logging.INFO, max_bytes=5 * 1024 * 1024, backup_count=5
):
    """
    Set up a logger with rotation and ensure the log directory exists.

    Args:
        name (str): Name of the logger.
        file_name (str): Name of the log file (without extension).
        level (int): Logging level.
        max_bytes (int): Maximum size of log file before rotation (default: 5MB).
        backup_count (int): Number of backup files to keep (default: 5).

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Get the directory of the current script file
    script_dir = Path(__file__).resolve().parent

    # Define the log directory relative to the script directory
    log_dir = script_dir / "../log"

    # Make sure the log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # Define log file path
    log_file = log_dir / f"{file_name}.log"

    # Define formatter with timestamp
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set up RotatingFileHandler
    handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    handler.setFormatter(formatter)

    # Get the logger and set level
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding multiple handlers to the logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
