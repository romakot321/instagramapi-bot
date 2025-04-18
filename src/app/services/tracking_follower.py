import datetime as dt
import types
from loguru import logger
from typing import Annotated

from aiogram3_di import Depends

from aiogram.types import CallbackQuery
from aiogram import types
from aiogram.methods import TelegramMethod

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.tracking import TrackingRepository
from app.schemas.action_callback import TrackingActionCallback, TrackingReportCallback
from app.schemas.message import TextMessage
from app.schemas.texts import (
    build_tracking_followers_text,
)
from app.services.utils import build_aiogram_method


class TrackingFollowerService:
    def __init__(
        self,
        tracking_repository: TrackingRepository,
        instagram_repository: InstagramRepository,
        keyboard_repository: KeyboardRepository,
        subscription_repository: SubscriptionRepository,
    ):
        self.tracking_repository = tracking_repository
        self.instagram_repository = instagram_repository
        self.keyboard_repository = keyboard_repository
        self.subscription_repository = subscription_repository

    @classmethod
    def init(
        cls,
        tracking_repository: Annotated[
            TrackingRepository, Depends(TrackingRepository.depend)
        ],
        instagram_repository: Annotated[
            InstagramRepository, Depends(InstagramRepository)
        ],
        keyboard_repository: Annotated[KeyboardRepository, Depends(KeyboardRepository)],
        subscription_repository: Annotated[
            SubscriptionRepository, Depends(SubscriptionRepository.init)
        ],
    ):
        return cls(
            tracking_repository=tracking_repository,
            instagram_repository=instagram_repository,
            keyboard_repository=keyboard_repository,
            subscription_repository=subscription_repository,
        )

    async def handle_tracking_followers(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        await query.answer("Функция в разработке")
        info = await self.instagram_repository.get_user_followers(data.username)
        message = TextMessage(
            text=build_tracking_followers_text(info),
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                data.username
            ),
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_tracking_new_subscribes(
        self, query: CallbackQuery, data: TrackingReportCallback
    ) -> TelegramMethod:
        followers_diff = await self.instagram_repository.get_user_followers_difference(
            data.username
        )
        report_date = dt.datetime.now().replace(hour=0, minute=0, second=0)

        subscribes_usernames = []
        for diff in followers_diff:
            if diff.report_id != data.report_id:
                continue
            subscribes_usernames += diff.subscribes_usernames
        paginated_subscribes = [
            subscribes_usernames[i : i + 25]
            for i in range(0, len(subscribes_usernames), 3)
        ]

        if not subscribes_usernames or len(paginated_subscribes) < data.page:
            message = TextMessage(text="Подписавшихся нет")
        else:
            message = TextMessage(
                text=build_tracking_followers_text(paginated_subscribes[data.page - 1]),
                reply_markup=self.keyboard_repository.build_tracking_new_subscribes_keyboard(
                    data.username, len(subscribes_usernames), data.page, on_page_count=25
                ),
                parse_mode="MarkdownV2"
            )
        return build_aiogram_method(None, tg_object=query, message=message, use_edit="отчет" not in query.message.text.lower())

    async def handle_tracking_new_unsubscribes(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        followers_diff = await self.instagram_repository.get_user_followers_difference(
            data.username
        )
        report_date = dt.datetime.now().replace(hour=0, minute=0, second=0)

        unsubscribes_usernames = []
        for diff in followers_diff:
            if diff.report_id != data.report_id:
                continue
            unsubscribes_usernames += diff.unsubscribes_usernames
        paginated_subscribes = [
            unsubscribes_usernames[i : i + 25]
            for i in range(0, len(unsubscribes_usernames), 3)
        ]

        if not unsubscribes_usernames or len(paginated_subscribes) < data.page:
            message = TextMessage(text="Отписавшихся нет")
        else:
            message = TextMessage(
                text=build_tracking_followers_text(paginated_subscribes[data.page - 1]),
                reply_markup=self.keyboard_repository.build_tracking_new_unsubscribes_keyboard(
                    data.username, len(unsubscribes_usernames), data.page, on_page_count=25
                ),
                parse_mode="MarkdownV2"
            )
        return build_aiogram_method(None, tg_object=query, message=message, use_edit="отчет" not in query.message.text.lower())
