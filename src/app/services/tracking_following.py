import datetime as dt
from loguru import logger
import types
from typing import Annotated, AsyncGenerator

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
    build_tracking_following_text,
)
from app.services.utils import build_aiogram_method


class TrackingFollowingService:
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

    async def handle_tracking_following(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        await query.answer("Функция в разработке")
        info = await self.instagram_repository.get_user_following(data.username)
        message = TextMessage(
            text=build_tracking_following_text(info),
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                data.username
            ),
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def _fetch_following_paginated(
        self, report_id: int, paginate_key: str, on_page_count: int = 25
    ) -> tuple[list[list[str]], int]:
        following_diff = (
            await self.instagram_repository.get_report_following_difference(report_id)
        )

        usernames = []
        for diff in following_diff:
            if diff.report_id != report_id:
                continue
            usernames += getattr(diff, paginate_key)
        paginated_usernames = [
            usernames[i : i + on_page_count]
            for i in range(0, len(usernames), on_page_count)
        ]
        return paginated_usernames, len(usernames)

    async def handle_tracking_following(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        await query.answer("Функция в разработке")
        info = await self.instagram_repository.get_user_following(data.username)
        message = TextMessage(
            text=build_tracking_following_text(info),
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                data.username
            ),
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def _handle_load_new_subscribes(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> AsyncGenerator[TelegramMethod]:
        yield build_aiogram_method(
            None,
            tg_object=query,
            message=TextMessage(text="Загружаю..."),
            use_edit=False,
        )

        paginated_subscribes, total_count = await self._fetch_following_paginated(
            data.report_id, "subscribes_usernames"
        )

        if not paginated_subscribes or len(paginated_subscribes) < data.page:
            message = TextMessage(text="Подписок нет")
        else:
            message = TextMessage(
                text=build_tracking_following_text(paginated_subscribes[data.page - 1]),
                reply_markup=self.keyboard_repository.build_tracking_subscribtions_keyboard(
                    data.username,
                    total_count,
                    data.page,
                    on_page_count=25,
                ),
                parse_mode="MarkdownV2",
            )

        yield build_aiogram_method(
            None,
            tg_object=query,
            message=message,
            use_edit="статистика" not in query.message.text.lower(),
        )

    async def _handle_show_new_subscribes(self, query, data):
        paginated_subscribes, total_count = await self._fetch_following_paginated(
            data.report_id, "subscribes_usernames"
        )

        if not paginated_subscribes or len(paginated_subscribes) < data.page:
            message = TextMessage(text="Подписок нет")
        else:
            message = TextMessage(
                text=build_tracking_following_text(paginated_subscribes[data.page - 1]),
                reply_markup=self.keyboard_repository.build_tracking_subscribtions_keyboard(
                    data.username,
                    total_count,
                    data.page,
                    on_page_count=25,
                ),
                parse_mode="MarkdownV2",
            )

        yield build_aiogram_method(
            None,
            tg_object=query,
            message=message,
            use_edit="статистика" not in query.message.text.lower(),
        )

    def handle_tracking_new_subscribes(
        self, query: CallbackQuery, data: TrackingReportCallback
    ) -> TelegramMethod:
        if "статистика" in query.message.text.lower():  # If it's not page change
            return self._handle_load_new_subscribes(query, data)
        return self._handle_show_new_subscribes(query, data)

    async def _handle_load_new_unsubscribes(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> AsyncGenerator[TelegramMethod]:
        yield build_aiogram_method(
            None,
            tg_object=query,
            message=TextMessage(text="Загружаю..."),
            use_edit=False,
        )

        paginated_subscribes, total_count = await self._fetch_following_paginated(
            data.report_id, "unsubscribes_usernames"
        )

        if not paginated_subscribes or len(paginated_subscribes) < data.page:
            message = TextMessage(text="Отписок нет")
        else:
            message = TextMessage(
                text=build_tracking_following_text(paginated_subscribes[data.page - 1]),
                reply_markup=self.keyboard_repository.build_tracking_unsubscribes_keyboard(
                    data.username,
                    total_count,
                    data.page,
                    on_page_count=25,
                ),
                parse_mode="MarkdownV2",
            )

        yield build_aiogram_method(
            None,
            tg_object=query,
            message=message,
            use_edit="статистика" not in query.message.text.lower(),
        )

    async def _handle_show_new_unsubscribes(self, query, data):
        paginated_subscribes, total_count = await self._fetch_following_paginated(
            data.report_id, "unsubscribes_usernames"
        )

        if not paginated_subscribes or len(paginated_subscribes) < data.page:
            message = TextMessage(text="Отписок нет")
        else:
            message = TextMessage(
                text=build_tracking_following_text(paginated_subscribes[data.page - 1]),
                reply_markup=self.keyboard_repository.build_tracking_unsubscribes_keyboard(
                    data.username,
                    total_count,
                    data.page,
                    on_page_count=25,
                ),
                parse_mode="MarkdownV2",
            )

        yield build_aiogram_method(
            None,
            tg_object=query,
            message=message,
            use_edit="статистика" not in query.message.text.lower(),
        )

    def handle_tracking_new_unsubscribes(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> AsyncGenerator[TelegramMethod]:
        if "статистика" in query.message.text.lower():  # If it's not page change
            return self._handle_load_new_unsubscribes(query, data)
        return self._handle_show_new_unsubscribes(query, data)
