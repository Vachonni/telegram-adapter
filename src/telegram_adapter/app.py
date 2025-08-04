import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from telegram_adapter.config.logs import setup_logging
from telegram_adapter.config.settings import settings
from telegram_adapter.utils import get_ollama

# Init logger
setup_logging()
logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Security check
    user_id = update.effective_user.id if update.effective_user else None
    if user_id not in settings.allowed_ids:
        logger.warning("Blocked user: %s", user_id)
        await update.message.reply_text("Vous n'êtes pas autorisé à utiliser ce bot.")  # type: ignore
        return
    # Log the received message
    message = update.message.text if update.message and update.message.text else None
    logger.debug("Message reçu : %s", message)
    # TODO: Adapter logic to come here
    llm = get_ollama()
    response = llm(message)
    # TODO: Adapter logic to come here
    await update.message.reply_text(f"J'ai reçu : {message}. Je réponds : {response}")  # type: ignore


def main():
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Handle only text messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Start bot
    logger.debug("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
