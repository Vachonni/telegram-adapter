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
from telegram_adapter.utils import (
    get_ollama,
    authorized_user,
    validate_file_upload,
    upload_file,
)

# Init logger
setup_logging()
logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Security check
    if not await authorized_user(update):
        return

    # Log the received message
    message = update.message.text if update.message and update.message.text else None
    logger.debug("Message reçu : %s", message)

    # TODO: Adapter logic to come here
    llm = get_ollama()
    response = llm(message)
    # TODO: Adapter logic to come here

    if update.message:
        await update.message.reply_text(
            f"J'ai reçu : {message}. Je réponds : {response}"
        )


async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle CSV, Excel, and PDF file uploads (documents only)"""
    # Security check
    if not await authorized_user(update):
        return

    # Check if message exists
    if not update.message:
        return

    # Validate file upload
    is_valid, error_message, file_name = validate_file_upload(update.message)
    if not is_valid or not file_name:
        await update.message.reply_text(
            error_message or "Erreur de validation du fichier."
        )
        return

    # Upload file
    upload_success, upload_error, unique_filename = await upload_file(
        update.message, context.bot, file_name
    )

    if upload_success and unique_filename:
        await update.message.reply_text(
            f"Fichier '{unique_filename}' téléchargé avec succès!"
        )
    else:
        await update.message.reply_text(
            upload_error or "Erreur lors du téléchargement."
        )


def main():
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Handle text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Handle file uploads (documents only - CSV and Excel files)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file_upload))

    # Start bot
    logger.debug("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
