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
from app.schemas.texts import build_media_info_list_text, build_user_info_text
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

    async def _handle_new_user(self, msg: Message):
        await self.user_repository.create(telegram_id=msg.from_user.id)
        message = TextMessage(text=start_text, reply_markup=self.keyboard_repository.build_main_keyboard())
        return build_aiogram_method(msg.from_user.id, message)

    async def _handle_main_menu_show(self, msg: Message):
        message = TextMessage(
            text="Выберите действие", reply_markup=self.keyboard_repository.build_main_keyboard()
        )
        return build_aiogram_method(msg.from_user.id, message)

    async def handle_user_start(self, msg: Message):
        if (await self.user_repository.get_by_telegram_id(msg.from_user.id)) is None:
            return await self._handle_new_user(msg)
        return await self._handle_main_menu_show(msg)

    async def handle_user_get(self, msg: Message, bot: Bot):
        message = TextMessage(
            text="Получение данных...",
        )
        method = build_aiogram_method(msg.from_user.id, message)
        inprogress_message = await bot(method)

        schema = await self.instagram_repository.get_user_info(msg.text.strip().lower())
        message = TextMessage(
            text=build_user_info_text(schema), message_id=inprogress_message.message_id
        )
        method = build_aiogram_method(msg.from_user.id, message, use_edit=True)
        await bot(method)

    async def handle_media_get(self, msg: Message, bot: Bot):
        message = TextMessage(
            text="Получение данных...",
        )
        method = build_aiogram_method(msg.from_user.id, message)
        inprogress_message = await bot(method)

        schemas = await self.instagram_repository.get_user_media_info(
            msg.text.strip().lower()
        )
        message = TextMessage(
            text=build_media_info_list_text(schemas),
            message_id=inprogress_message.message_id,
        )
        method = build_aiogram_method(msg.from_user.id, message, use_edit=True)
        await bot(method)
