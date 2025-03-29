import types
from typing import Annotated, AsyncGenerator, Generator
from urllib.parse import urlparse

from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import types as types
from aiogram.methods import EditMessageText, TelegramMethod

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.tracking import TrackingRepository
from app.schemas.action_callback import Action, TrackingActionCallback
from app.schemas.forms import TrackingCreateForm
from app.schemas.message import TextMessage
from app.schemas.texts import build_user_followers_text, build_user_info_masked_text, build_user_info_text, build_user_stats_text, start_text
from app.services.utils import build_aiogram_method


class TrackingService:
    def __init__(
        self,
        tracking_repository: TrackingRepository,
        instagram_repository: InstagramRepository,
        keyboard_repository: KeyboardRepository,
        subscription_repository: SubscriptionRepository
    ):
        self.tracking_repository = tracking_repository
        self.instagram_repository = instagram_repository
        self.keyboard_repository = keyboard_repository
        self.subscription_repository = subscription_repository

    @classmethod
    def init(
        cls,
        tracking_repository: Annotated[TrackingRepository, Depends(TrackingRepository.depend)],
        instagram_repository: Annotated[
            InstagramRepository, Depends(InstagramRepository)
        ],
        keyboard_repository: Annotated[KeyboardRepository, Depends(KeyboardRepository)],
        subscription_repository: Annotated[SubscriptionRepository, Depends(SubscriptionRepository.init)],
    ):
        return cls(
            tracking_repository=tracking_repository,
            instagram_repository=instagram_repository,
            keyboard_repository=keyboard_repository,
            subscription_repository=subscription_repository
        )

    def _extract_username(self, user_input: str) -> str | None:
        url = urlparse(user_input)
        if url.netloc == '':
            return user_input
        elif url.netloc != "instagram.com":
            return None
        return url.path.strip("/")

    async def handle_form_create(self, query: CallbackQuery, fsm_context: FSMContext) -> TelegramMethod:
        await fsm_context.set_state(TrackingCreateForm.typing_username)
        message = TextMessage(text="Введите ссылку или имя пользователя", message_id=query.message.message_id)
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_create(self, msg: Message, fsm_context: FSMContext) -> AsyncGenerator[TelegramMethod]:
        username = self._extract_username(msg.text)
        if username is None:
            yield build_aiogram_method(msg.from_user.id, TextMessage(text="Неверная ссылка или пользователь не существует"))
            return

        await fsm_context.clear()
        message = TextMessage(text="Загружаем данные...")
        yield build_aiogram_method(msg.from_user.id, message)

        info = await self.instagram_repository.get_user_info(username)

        if not (await self.subscription_repository.get_by_telegram_id(msg.from_user.id, active=True)):
            yield await self._handle_show_without_subscription(msg, TrackingActionCallback(username=username, action=""))
        else:
            yield await self._handle_show_with_subscription(msg, TrackingActionCallback(username=username, action=""))

    async def handle_tracking_subscribe(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        user_trackings_count = await self.tracking_repository.count(creator_telegram_id=query.from_user.id)
        if user_trackings_count >= 1:
            message = TextMessage(
                text="Вы достигли максимального количества отслеживаний",
                reply_markup=self.keyboard_repository.build_to_paywall_keyboard(),
                message_id=query.message.message_id
            )
        else:
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
        if not (await self.subscription_repository.get_by_telegram_id(query.from_user.id, active=True)):
            return await self._handle_show_without_subscription(query, data)
        return await self._handle_show_with_subscription(query, data)

    async def _handle_show_with_subscription(self, tg_object: CallbackQuery | Message, data: TrackingActionCallback) -> TelegramMethod:
        subscribed = (await self.tracking_repository.get(tg_object.from_user.id, data.username, mute_not_found_exception=True)) is not None
        info = await self.instagram_repository.get_user_info(data.username)
        message = TextMessage(
            text=build_user_info_text(info),
            reply_markup=self.keyboard_repository.build_tracking_keyboard(data.username, subscribed),
            message_id=(tg_object.message.message_id if isinstance(tg_object, CallbackQuery) else None)
        )
        return build_aiogram_method(tg_object.from_user.id, message, use_edit=isinstance(tg_object, CallbackQuery))

    async def _handle_show_without_subscription(self, tg_object: CallbackQuery | Message, data: TrackingActionCallback) -> TelegramMethod:
        info = await self.instagram_repository.get_user_info(data.username)
        message = TextMessage(
            text=build_user_info_masked_text(info),
            reply_markup=self.keyboard_repository.build_tracking_show_full_keyboard(),
            message_id=(tg_object.message.message_id if isinstance(tg_object, CallbackQuery) else None)
        )
        return build_aiogram_method(tg_object.from_user.id, message, use_edit=isinstance(tg_object, CallbackQuery))

    async def handle_tracking_followers(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        info = await self.instagram_repository.get_user_followers(data.username)
        message = TextMessage(
            text=build_user_followers_text(info),
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(data.username),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_tracking_stats(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        user_info = await self.instagram_repository.get_user_info(data.username)
        user_stats = await self.instagram_repository.get_user_stats(data.username)
        media_stats = await self.instagram_repository.get_media_user_stats(data.username)
        message = TextMessage(
            text=build_user_stats_text(user_stats, media_stats, user_info),
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(data.username),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_report_trackings(self, query: CallbackQuery) -> list[TelegramMethod]:
        methods = []
        for tracking in (await self.tracking_repository.list(creator_telegram_id=query.from_user.id)):
            user_info = await self.instagram_repository.get_user_info(tracking.instagram_username)
            user_stats = await self.instagram_repository.get_user_stats(tracking.instagram_username)
            media_stats = await self.instagram_repository.get_media_user_stats(tracking.instagram_username)
            message = TextMessage(
                text="Отчет по " + tracking.instagram_username + "\n\n" + build_user_stats_text(user_stats, media_stats, user_info),
            )
            methods.append(build_aiogram_method(query.from_user.id, message))
        return methods
