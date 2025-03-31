import types
from typing import Annotated

from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram import types as types
from aiogram.methods import EditMessageText, TelegramMethod

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.user import UserRepository
from app.schemas.action_callback import Action, SubscriptionActionCallback
from app.schemas.message import TextMessage
from app.schemas.texts import build_subscription_info_text, subscription_paywall_text
from app.services.utils import build_aiogram_method
from db.tables import Subscription


class SubscriptionService:
    def __init__(
        self,
        subscription_repository: SubscriptionRepository,
        keyboard_repository: KeyboardRepository,
        user_repository: UserRepository,
    ):
        self.subscription_repository = subscription_repository
        self.keyboard_repository = keyboard_repository
        self.user_repository = user_repository

    @classmethod
    def init(
        cls,
        subscription_repository: Annotated[
            SubscriptionRepository, Depends(SubscriptionRepository.depend)
        ],
        keyboard_repository: Annotated[KeyboardRepository, Depends(KeyboardRepository)],
        user_repository: Annotated[UserRepository, Depends(UserRepository.init)],
    ):
        return cls(
            subscription_repository=subscription_repository,
            keyboard_repository=keyboard_repository,
            user_repository=user_repository,
        )

    async def _handle_new_subscription(self, query: CallbackQuery) -> TelegramMethod:
        message = TextMessage(
            text="У вас нет активной подписки",
            reply_markup=self.keyboard_repository.build_to_paywall_keyboard(),
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def _handle_subscription_menu_show(
        self, query: CallbackQuery, subscriptions: list[Subscription]
    ) -> TelegramMethod:
        newest_subscription = max(subscriptions, key=lambda i: i.expire_at)
        message = TextMessage(
            text=build_subscription_info_text(newest_subscription),
            reply_markup=self.keyboard_repository.build_subscription_menu_keyboard(),
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_subscription_menu(self, query: CallbackQuery) -> TelegramMethod:
        subscriptions = await self.subscription_repository.get_by_telegram_id(
            query.from_user.id, active=True
        )
        if not subscriptions:
            return await self._handle_new_subscription(query)
        return await self._handle_subscription_menu_show(query, subscriptions)

    async def handle_subscription_add(self, tg_object: CallbackQuery | Message) -> TelegramMethod:
        message = TextMessage(
            text=subscription_paywall_text,
            reply_markup=self.keyboard_repository.build_paywall_keyboard(),
            message_id=tg_object.message.message_id if isinstance(tg_object, CallbackQuery) else None,
        )
        return build_aiogram_method(tg_object.from_user.id, message, use_edit=isinstance(tg_object, CallbackQuery))

    async def handle_subscription_add_created(
        self, query: CallbackQuery, data: SubscriptionActionCallback
    ) -> TelegramMethod:
        message = TextMessage(text="Оплата получена")
        return build_aiogram_method(query.from_user.id, message)
