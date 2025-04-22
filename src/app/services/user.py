import types
from typing import Annotated
from urllib import parse

from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram import types as types
from aiogram.methods import EditMessageText, TelegramMethod

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.user import UserRepository
from app.schemas.action_callback import Action
from app.schemas.message import PhotoMessage, TextMessage
from app.schemas.texts import build_start_text
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

    def _get_referral_id(self, tg_object: Message | CallbackQuery) -> str | None:
        if isinstance(tg_object, Message) and tg_object.text:
            return " ".join(tg_object.text.split(" ")[1:])

    async def _handle_new_user(self, tg_object: Message | CallbackQuery) -> list[TelegramMethod]:
        await self.user_repository.create(
            telegram_id=tg_object.from_user.id,
            telegram_name=tg_object.from_user.full_name,
            telegram_username=tg_object.from_user.username,
            referral_id=self._get_referral_id(tg_object)
        )
        message1 = PhotoMessage(
            photo=FSInputFile("static/start.jpg"),
            reply_markup=self.keyboard_repository.build_main_keyboard(),
        )
        message2 = TextMessage(
            text=build_start_text(tg_object.from_user.id),
            reply_markup=self.keyboard_repository.build_to_add_tracking_keyboard(),
            parse_mode="MarkdownV2",
        )
        return [build_aiogram_method(tg_object.from_user.id, message1), build_aiogram_method(tg_object.from_user.id, message2)]

    async def _handle_main_menu_show(self, tg_object: Message | CallbackQuery) -> list[TelegramMethod]:
        message1 = PhotoMessage(
            photo=FSInputFile("static/start.jpg"),
            reply_markup=self.keyboard_repository.build_main_keyboard(),
        )
        message2 = TextMessage(
            text=build_start_text(tg_object.from_user.id),
            reply_markup=self.keyboard_repository.build_to_add_tracking_keyboard(),
            parse_mode="MarkdownV2"
        )
        if isinstance(tg_object, CallbackQuery):
            return [build_aiogram_method(None, tg_object=tg_object, message=message2)]
        else:
            return [build_aiogram_method(tg_object.from_user.id, message1), build_aiogram_method(tg_object.from_user.id, message2)]

    async def handle_user_start(self, tg_object: Message | CallbackQuery) -> list[TelegramMethod]:
        if (
            await self.user_repository.get_by_telegram_id(tg_object.from_user.id)
        ) is None:
            return await self._handle_new_user(tg_object)
        return await self._handle_main_menu_show(tg_object)
