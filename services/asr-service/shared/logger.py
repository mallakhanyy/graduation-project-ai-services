import logging
from shared.config import settings


def get_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] "
        "%(levelname)s "
        "%(name)s: "
        "%(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(
        settings.logging.level
    )

    return logger

logger = get_logger(
    settings.service.name
)