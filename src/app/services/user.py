import types
from typing import Annotated

from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram import types as types
from aiogram.methods import EditMessageText

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.user import UserRepository
from app.schemas.action_callback import Action
from app.schemas.message import TextMessage
from app.schemas.texts import start_text
from app.services.utils import build_aiogram_method


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        instagram_repository: InstagramRepository,
        keyboard_repository: KeyboardRepository,
    ):
        self.user_repository = user_repository
        self.instagram_repository = instagram_repository
        self.keyboard_repository = keyboard_repository

    @classmethod
    def init(
        cls,
        user_repository: Annotated[UserRepository, Depends(UserRepository.depend)],
        instagram_repository: Annotated[
            InstagramRepository, Depends(InstagramRepository)
        ],
        keyboard_repository: Annotated[KeyboardRepository, Depends(KeyboardRepository)],
    ):
        return cls(
            user_repository=user_repository,
            instagram_repository=instagram_repository,
            keyboard_repository=keyboard_repository,
        )

    async def _handle_new_user(self, tg_object: Message | CallbackQuery):
        await self.user_repository.create(telegram_id=tg_object.from_user.id)
        message = TextMessage(
            text=start_text,
            reply_markup=self.keyboard_repository.build_main_keyboard(),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(tg_object.from_user.id, message)

    async def _handle_main_menu_show(self, tg_object: Message | CallbackQuery):
        message = TextMessage(
            text="Выберите действие",
            reply_markup=self.keyboard_repository.build_main_keyboard(),
            message_id=(
                tg_object.message.message_id
                if isinstance(tg_object, CallbackQuery)
                else None
            ),
        )
        return build_aiogram_method(
            tg_object.from_user.id,
            message,
            use_edit=isinstance(tg_object, CallbackQuery),
        )

    async def handle_user_start(self, tg_object: Message | CallbackQuery):
        if (
            await self.user_repository.get_by_telegram_id(tg_object.from_user.id)
        ) is None:
            return await self._handle_new_user(tg_object)
        return await self._handle_main_menu_show(tg_object)
