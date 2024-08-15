import logging


def create_logger(name: str, filename: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Create a logger with the specified name, log file, and log level.
    Args:
        name (str): The name of the logger.
        filename (str): The path to the log file.
        level (int, optional): The log level. Defaults to logging.DEBUG.
    Returns:
        logging.Logger: The created logger.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.FileHandler(f"/log/{filename}")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger
