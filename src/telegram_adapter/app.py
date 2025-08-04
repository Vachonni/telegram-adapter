import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from telegram_adapter.config.logging import setup_logging
from telegram_adapter.config.settings import settings
from telegram_adapter.utils import get_ollama

# Init logger
setup_logging()
logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        message = update.message.text
        logger.debug("Message reçu : %s", message)
        logger.debug("Chat ID: %s", update.effective_chat.id)
        # TODO: Adapter logic to come here
        llm = get_ollama()
        response = llm(message)
        # TODO: Adapter logic to come here
        await update.message.reply_text(
            f"J'ai reçu : {message}. Je réponds : {response}"
        )
    else:
        logger.debug("No message or text found in update: %s", update)


def main():
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Gérer tous les messages texte
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Démarrer le bot
    logger.debug("Bot démarré...")
    app.run_polling()


if __name__ == "__main__":
    main()
