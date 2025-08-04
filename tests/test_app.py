import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from telegram import Update, Message, User
from telegram import Chat
from telegram.ext import ContextTypes
from telegram_adapter.app import handle_message
from datetime import datetime


class DummySettings:
    TELEGRAM_BOT_TOKEN = "dummy_token"
    allowed_ids = [12345]


@pytest.mark.asyncio
@patch("telegram_adapter.app.settings", new=DummySettings)
@patch(
    "telegram_adapter.app.get_ollama", return_value=lambda msg: "mocked Ollama response"
)
@patch.object(Message, "reply_text", new_callable=AsyncMock)
async def test_handle_message_authorized(mock_reply_text, mock_ollama):
    user = User(id=12345, first_name="Test", is_bot=False)
    chat = Chat(id=1, type="private")
    message = Message(
        message_id=1, date=datetime.now(), chat=chat, text="Hello", from_user=user
    )
    update = Update(update_id=1, message=message)
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await handle_message(update, context)
    mock_reply_text.assert_awaited_with(
        "J'ai reçu : Hello. Je réponds : mocked Ollama response"
    )


@pytest.mark.asyncio
@patch("telegram_adapter.app.settings", new=DummySettings)
@patch.object(Message, "reply_text", new_callable=AsyncMock)
async def test_handle_message_unauthorized(mock_reply_text):
    user = User(id=99999, first_name="Blocked", is_bot=False)
    chat = Chat(id=1, type="private")
    message = Message(
        message_id=1, date=datetime.now(), chat=chat, text="Blocked", from_user=user
    )
    update = Update(update_id=1, message=message)
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await handle_message(update, context)
    mock_reply_text.assert_awaited_with("Vous n'êtes pas autorisé à utiliser ce bot.")
