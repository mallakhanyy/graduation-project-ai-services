"""
logger.py
----------
Central logging configuration for the ASR Service.

Responsibilities:
- Configure application logging
- Create one shared logger
- Provide consistent log formatting
"""

import logging

from config import settings


logging.basicConfig(
    level=settings.logging.level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(settings.service.name)