import logging
from pathlib import Path
from datetime import datetime

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


async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle CSV, Excel, and PDF file uploads (documents only)"""
    # Security check
    user_id = update.effective_user.id if update.effective_user else None
    if user_id not in settings.allowed_ids:
        logger.warning("Blocked user trying to upload file: %s", user_id)
        if update.message:
            await update.message.reply_text(
                "Vous n'êtes pas autorisé à utiliser ce bot."
            )
        return

    # Check if message exists
    if not update.message:
        return

    # Get the document from the message
    if not update.message.document:
        await update.message.reply_text(
            "Seuls les documents sont acceptés, pas de photos, vidéos, audio, etc."
        )
        return

    file_obj = update.message.document
    file_name = (
        file_obj.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    logger.debug(
        "Document received: %s (size: %s bytes)", file_name, file_obj.file_size
    )

    # File size validation
    if file_obj.file_size and file_obj.file_size > settings.max_file_size_bytes:
        await update.message.reply_text(
            f"Fichier trop volumineux. Taille maximale autorisée: {settings.max_file_size_mb}MB"
        )
        return

    # File type validation (basic extension check)
    file_extension = Path(file_name).suffix.lower()

    if file_extension and file_extension not in settings.allowed_extensions_set:
        await update.message.reply_text(
            f"Type de fichier non autorisé: {file_extension}. Seuls les fichiers CSV (.csv), Excel (.xls, .xlsx) et PDF (.pdf) sont acceptés."
        )
        return

    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.upload_dir_path)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Get the file from Telegram
        telegram_file = await context.bot.get_file(file_obj.file_id)

        # Create unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_stem = Path(file_name).stem
        file_extension = Path(file_name).suffix
        unique_filename = f"{file_stem}_{timestamp}{file_extension}"

        # Save the file
        file_path = upload_dir / unique_filename
        await telegram_file.download_to_drive(file_path)

        logger.info("File saved successfully: %s", file_path)
        await update.message.reply_text(
            f"Fichier '{unique_filename}' téléchargé avec succès!"
        )

    except Exception as e:
        logger.error("Error uploading file: %s", str(e))
        await update.message.reply_text("Erreur lors du téléchargement du fichier.")


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
