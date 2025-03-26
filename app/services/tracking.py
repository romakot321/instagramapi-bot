import types
from typing import Annotated, AsyncGenerator, Generator

from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import types as types
from aiogram.methods import EditMessageText, TelegramMethod

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.tracking import TrackingRepository
from app.schemas.action_callback import Action, TrackingActionCallback
from app.schemas.forms import TrackingCreateForm
from app.schemas.message import TextMessage
from app.schemas.texts import build_user_followers_text, build_user_info_text, build_user_stats_text, start_text
from app.services.utils import build_aiogram_method


class TrackingService:
    def __init__(
        self,
        tracking_repository: TrackingRepository,
        instagram_repository: InstagramRepository,
        keyboard_repository: KeyboardRepository,
    ):
        self.tracking_repository = tracking_repository
        self.instagram_repository = instagram_repository
        self.keyboard_repository = keyboard_repository

    @classmethod
    def init(
        cls,
        tracking_repository: Annotated[TrackingRepository, Depends(TrackingRepository.depend)],
        instagram_repository: Annotated[
            InstagramRepository, Depends(InstagramRepository)
        ],
        keyboard_repository: Annotated[KeyboardRepository, Depends(KeyboardRepository)],
    ):
        return cls(
            tracking_repository=tracking_repository,
            instagram_repository=instagram_repository,
            keyboard_repository=keyboard_repository,
        )

    async def handle_form_create(self, query: CallbackQuery, fsm_context: FSMContext) -> TelegramMethod:
        await fsm_context.set_state(TrackingCreateForm.typing_username)
        message = TextMessage(text="Введите ссылку или имя пользователя", message_id=query.message.message_id)
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_create(self, msg: Message, fsm_context: FSMContext) -> AsyncGenerator[TelegramMethod]:
        await fsm_context.clear()
        message = TextMessage(text="Загружаем данные...")
        yield build_aiogram_method(msg.from_user.id, message)

        info = await self.instagram_repository.get_user_info(msg.text.strip())

        message = TextMessage(
            text=build_user_info_text(info),
            reply_markup=self.keyboard_repository.build_tracking_keyboard(info.username)
        )
        yield build_aiogram_method(msg.from_user.id, message)

    async def handle_tracking_subscribe(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        await self.tracking_repository.create(instagram_username=data.username, creator_telegram_id=query.from_user.id)
        message = TextMessage(
            text="Вы успешно подписались на пользователя @" + data.username,
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(data.username),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_show_trackings(self, query: CallbackQuery) -> TelegramMethod:
        trackings = await self.tracking_repository.list(creator_telegram_id=query.from_user.id)
        message = TextMessage(
            text="Ваши отслеживания",
            reply_markup=self.keyboard_repository.build_trackings_list_keyboard(trackings),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_show(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        info = await self.instagram_repository.get_user_info(data.username)
        message = TextMessage(
            text=build_user_info_text(info),
            reply_markup=self.keyboard_repository.build_tracking_keyboard(data.username),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_tracking_followers(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        info = await self.instagram_repository.get_user_followers(data.username)
        message = TextMessage(
            text=build_user_followers_text(info),
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(data.username),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_tracking_stats(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        info = await self.instagram_repository.get_user_stats(data.username)
        message = TextMessage(
            text=build_user_stats_text(info),
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(data.username),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

