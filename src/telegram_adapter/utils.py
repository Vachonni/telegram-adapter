import logging

from telegram_adapter.config.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
