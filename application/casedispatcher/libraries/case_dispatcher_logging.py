import logging
from pathlib import Path


def setup_logger(name, file_name, level=logging.INFO):
    """Function setup as many loggers as you want"""
    # Get the directory of the current script file
    script_dir = Path(__file__).resolve().parent

    # Define the log directory relative to the script directory
    log_dir = script_dir / "../log"

    # Make sure the log directory exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # Define log file
    log_file = log_dir / f"{file_name}.log"
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
