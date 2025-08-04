import logging

from langchain_community.llms import Ollama

from telegram_adapter.config.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def get_ollama():
    # Configuration du modèle Ollama
    llm = Ollama(model="llama3.2:3b", base_url="http://localhost:11434")

    return llm
