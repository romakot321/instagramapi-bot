from aiogram.methods import TelegramMethod
from aiogram.types import Message

from app.schemas.message import TextMessage
from app.schemas.texts import support_text
from app.services.utils import build_aiogram_method


class SupportService:
    def __init__(self):
        pass

    @classmethod
    async def init(cls):
        return cls()

    async def handle_support_menu(self, msg: Message) -> TelegramMethod:
        message = TextMessage(
            text=support_text,
            parse_mode="MarkdownV2"
        )
        return build_aiogram_method(None, tg_object=msg, message=message)
