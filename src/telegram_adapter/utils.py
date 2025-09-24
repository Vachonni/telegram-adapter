import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

from langchain_community.llms import Ollama
from telegram import Update, Message

from telegram_adapter.config.logs import setup_logging
from telegram_adapter.config.settings import settings

setup_logging()
logger = logging.getLogger(__name__)


def get_ollama():
    # Configuration du modèle Ollama
    llm = Ollama(model="llama3.2:3b", base_url="http://localhost:11434")

    return llm


async def authorized_user(update: Update) -> bool:
    """
    Check if user is authorized and send unauthorized message if not.

    Returns:
        bool: True if authorized, False if not authorized
    """
    user_id = update.effective_user.id if update.effective_user else None
    is_authorized = user_id in settings.allowed_ids

    if not is_authorized:
        logger.warning("Blocked user: %s", user_id)
        if update.message:
            await update.message.reply_text(
                "Vous n'êtes pas autorisé à utiliser ce bot."
            )
        return False
    return True


def validate_file_upload(message: Message) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate file upload from message.

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
        - Success (True/False)
        - Error message if validation fails
        - File name if validation succeeds
    """
    # Check if it's a document
    if not message.document:
        return (
            False,
            "Seuls les documents sont acceptés, pas de photos, vidéos, audio, etc.",
            None,
        )

    file_obj = message.document
    file_name = (
        file_obj.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    logger.debug(
        "Document received: %s (size: %s bytes)", file_name, file_obj.file_size
    )

    # File size validation
    if file_obj.file_size and file_obj.file_size > settings.max_file_size_bytes:
        return (
            False,
            f"Fichier trop volumineux. Taille maximale autorisée: {settings.max_file_size_mb}MB",
            None,
        )

    # File type validation
    file_extension = Path(file_name).suffix.lower()
    if file_extension and file_extension not in settings.allowed_extensions_set:
        return (
            False,
            f"Type de fichier non autorisé: {file_extension}. Seuls les fichiers CSV (.csv), Excel (.xls, .xlsx) et PDF (.pdf) sont acceptés.",
            None,
        )

    return True, None, file_name


async def upload_file(
    message: Message, bot, file_name: str
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Upload file to the configured upload directory.

    Args:
        message: Telegram message containing the document
        bot: Telegram bot instance
        file_name: Name of the file to upload

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
        - Success (True/False)
        - Error message if upload fails
        - Unique filename if upload succeeds
    """
    try:
        # Ensure message has a document
        if not message.document:
            return False, "Aucun document trouvé dans le message.", None

        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.upload_dir_path)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Get the file from Telegram
        telegram_file = await bot.get_file(message.document.file_id)

        # Create unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_stem = Path(file_name).stem
        file_extension = Path(file_name).suffix
        unique_filename = f"{file_stem}_{timestamp}{file_extension}"

        # Save the file
        file_path = upload_dir / unique_filename
        await telegram_file.download_to_drive(file_path)

        logger.info("File saved successfully: %s", file_path)
        return True, None, unique_filename

    except Exception as e:
        logger.error("Error uploading file: %s", str(e))
        return False, "Erreur lors du téléchargement du fichier.", None
