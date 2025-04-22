import datetime as dt
from typing import Annotated, AsyncGenerator
from urllib.parse import urlparse

from aiogram3_di import Depends

from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.methods import TelegramMethod

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.tariff import TariffRepository
from app.repositories.tracking import TrackingRepository
from app.schemas.action_callback import (
    Action,
    TrackingActionCallback,
    TrackingReportCallback,
)
from app.schemas.forms import TrackingCreateForm
from app.schemas.instagram import InstagramUserSchema
from app.schemas.message import TextMessage
from app.schemas.texts import (
    build_big_tracking_info_text,
    build_tracking_followers_text,
    build_tracking_info_masked_text,
    build_tracking_info_text,
    build_tracking_not_found_text,
    build_tracking_private_text,
    build_tracking_report_text,
    build_tracking_stats_text,
    build_tracking_subscribe_text,
    build_tracking_unsubscribe_text,
    tracking_big_subscribe_text
)
from app.services.utils import build_aiogram_method


class TrackingService:
    def __init__(
        self,
        tracking_repository: TrackingRepository,
        instagram_repository: InstagramRepository,
        keyboard_repository: KeyboardRepository,
        subscription_repository: SubscriptionRepository,
        tariff_repository: TariffRepository,
    ):
        self.tracking_repository = tracking_repository
        self.instagram_repository = instagram_repository
        self.keyboard_repository = keyboard_repository
        self.subscription_repository = subscription_repository
        self.tariff_repository = tariff_repository

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
        tariff_repository: Annotated[TariffRepository, Depends(TariffRepository.init)],
    ):
        return cls(
            tracking_repository=tracking_repository,
            instagram_repository=instagram_repository,
            keyboard_repository=keyboard_repository,
            subscription_repository=subscription_repository,
            tariff_repository=tariff_repository,
        )

    def _extract_username(self, user_input: str) -> str | None:
        user_input = user_input.lower().lstrip("@")
        url = urlparse(user_input)
        if url.netloc == "":
            return user_input
        elif url.netloc != "instagram.com" and url.netloc != "www.instagram.com":
            return None
        return url.path.strip("/")

    async def handle_form_create(
        self, tg_object: CallbackQuery | Message, fsm_context: FSMContext
    ) -> TelegramMethod:
        await fsm_context.set_state(TrackingCreateForm.typing_username)
        message = TextMessage(text="Введите ссылку или имя пользователя")
        return build_aiogram_method(None, tg_object=tg_object, message=message)

    async def handle_create(
        self, msg: Message, fsm_context: FSMContext
    ) -> AsyncGenerator[TelegramMethod]:
        username = self._extract_username(msg.text)
        if username is None:
            yield build_aiogram_method(
                msg.from_user.id,
                TextMessage(text="Неверная ссылка или пользователь не существует"),
            )
            return

        await fsm_context.clear()
        message = TextMessage(
            text="Загружаем данные... Если аккаунт добавлен впервые - придется подождать, пока мы соберем все данные"
        )
        yield build_aiogram_method(msg.from_user.id, message)

        info = await self.instagram_repository.start_user_tracking(username)
        if isinstance(info, str):  # Error occured
            message = TextMessage(
                text=info,
                reply_markup=self.keyboard_repository.build_to_add_tracking_keyboard(),
            )
            yield build_aiogram_method(msg.from_user.id, message)
        elif not (
            await self.subscription_repository.get_by_telegram_id(
                msg.from_user.id, active=True
            )
        ):
            yield await self._handle_show_without_subscription(
                msg, TrackingActionCallback(username=username, action="")
            )
        else:
            yield await self._handle_show_with_subscription(
                msg, TrackingActionCallback(username=username, action="")
            )

    async def handle_tracking_subscribe(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        user_subscriptions = await self.subscription_repository.get_by_telegram_id(
            query.from_user.id, active=True
        )
        subscription_id = None
        for subscription in user_subscriptions:
            if subscription.tracking_username == data.username:
                subscription_id = subscription.id
                break
            if subscription.tracking_username is None:
                subscription_id = subscription.id

        if subscription_id is None:
            message = TextMessage(
                text="Вы достигли максимального количества отслеживаний",
                reply_markup=self.keyboard_repository.build_to_trackings_max_buy_keyboard(
                    data.username
                ),
            )
        elif (await self.instagram_repository.get_user_info(data.username)).is_big():
            message = TextMessage(
                text=tracking_big_subscribe_text,
                reply_markup=self.keyboard_repository.build_to_add_tracking_keyboard(),
            )
        else:
            await self.subscription_repository.update(
                subscription_id, tracking_username=data.username
            )
            await self.tracking_repository.create(
                instagram_username=data.username,
                creator_telegram_id=query.from_user.id,
            )
            message = TextMessage(
                text=build_tracking_subscribe_text(
                    data.username, int(subscription.tariff.tracking_report_interval)
                ),
                reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                    data.username
                ),
                parse_mode="MarkdownV2",
            )

        return build_aiogram_method(None, tg_object=query, message=message)

    async def handle_tracking_unsubscribe(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        await self.tracking_repository.delete(query.from_user.id, data.username)
        message = TextMessage(
            text=build_tracking_unsubscribe_text(data.username),
            reply_markup=self.keyboard_repository.build_to_trackings_list_keyboard(),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(None, message=message, tg_object=query)

    def _handle_show_trackings_empty(
        self, tg_object: CallbackQuery | Message
    ) -> TelegramMethod:
        message = TextMessage(
            text="У вас нет отслеживаний",
            reply_markup=self.keyboard_repository.build_to_add_tracking_keyboard(),
        )
        return build_aiogram_method(None, message=message, tg_object=tg_object)

    async def handle_show_trackings(
        self, tg_object: CallbackQuery | Message
    ) -> TelegramMethod:
        trackings = await self.tracking_repository.list(
            creator_telegram_id=tg_object.from_user.id
        )
        if not trackings:
            return self._handle_show_trackings_empty(tg_object)

        message = TextMessage(
            text="Ваши отслеживания",
            reply_markup=self.keyboard_repository.build_trackings_list_keyboard(
                trackings
            ),
        )
        return build_aiogram_method(None, message=message, tg_object=tg_object)

    async def handle_settings(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        tariffs = await self.tariff_repository.list()
        subscription = await self.subscription_repository.get(
            user_telegram_id=query.from_user.id, tracking_username=data.username
        )
        message = TextMessage(
            text="Настройки отслеживания пользователя " + data.username,
            reply_markup=self.keyboard_repository.build_tracking_settings_keyboard(
                data.username, tariffs, subscription.tariff_id
            ),
        )
        return build_aiogram_method(None, tg_object=query, message=message)

    async def handle_show(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        if not (
            await self.subscription_repository.get_by_telegram_id(
                query.from_user.id, active=True
            )
        ):
            return await self._handle_show_without_subscription(query, data)
        return await self._handle_show_with_subscription(query, data)

    def _handle_show_private_tracking(
        self, tg_object: CallbackQuery | Message, info: InstagramUserSchema
    ):
        message = TextMessage(
            text=build_tracking_private_text(info),
            reply_markup=self.keyboard_repository.build_to_add_tracking_keyboard(),
        )
        return build_aiogram_method(None, message=message, tg_object=tg_object)

    def _handle_show_big_tracking(
        self,
        tg_object: CallbackQuery | Message,
        info: InstagramUserSchema,
    ):
        message = TextMessage(
            text=build_big_tracking_info_text(info),
            reply_markup=self.keyboard_repository.build_tracking_keyboard(
                info.username, False
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(None, message=message, tg_object=tg_object)

    def _handle_show_tracking_not_found(
        self, tg_object: CallbackQuery | Message, tracking_username: str
    ) -> TelegramMethod:
        message = TextMessage(
            text=build_tracking_not_found_text(tracking_username),
            reply_markup=self.keyboard_repository.build_to_add_tracking_keyboard(),
        )
        return build_aiogram_method(None, message=message, tg_object=tg_object)

    async def _handle_show_with_subscription(
        self, tg_object: CallbackQuery | Message, data: TrackingActionCallback
    ) -> TelegramMethod:
        subscribed = (
            await self.tracking_repository.get(
                tg_object.from_user.id, data.username, mute_not_found_exception=True
            )
        ) is not None

        info = await self.instagram_repository.get_user_info(data.username)
        if info is None:
            return self._handle_show_tracking_not_found(tg_object, data.username)
        if info.is_private:
            return self._handle_show_private_tracking(tg_object, info)
        if info.is_big() and not subscribed:
            return self._handle_show_big_tracking(tg_object, info)

        message = TextMessage(
            text=build_tracking_info_text(info),
            reply_markup=self.keyboard_repository.build_tracking_keyboard(
                data.username, subscribed
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(None, message=message, tg_object=tg_object)

    async def _handle_show_without_subscription(
        self, tg_object: CallbackQuery | Message, data: TrackingActionCallback
    ) -> TelegramMethod:
        info = await self.instagram_repository.get_user_info(data.username)
        if info is None:
            return self._handle_show_tracking_not_found(tg_object, data.username)
        message = TextMessage(
            text=build_tracking_info_masked_text(info),
            reply_markup=self.keyboard_repository.build_tracking_show_full_keyboard(
                data.username
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(
            None,
            tg_object=tg_object,
            message=message,
        )

    async def handle_tracking_stats(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        user_info = await self.instagram_repository.get_user_info(data.username)
        user_stats = await self.instagram_repository.get_user_stats(data.username)
        if isinstance(user_stats, str):
            return build_aiogram_method(
                None,
                message=TextMessage(
                    text=user_stats,
                    reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                        data.username
                    ),
                ),
                tg_object=query,
                use_edit=True,
            )

        weekly_media_stats = await self.instagram_repository.get_media_user_stats(
            data.username, days=7
        )
        if isinstance(weekly_media_stats, str):
            return build_aiogram_method(
                None,
                message=TextMessage(
                    text=weekly_media_stats,
                    reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                        data.username
                    ),
                ),
                tg_object=query,
                use_edit=True,
            )

        monthly_media_stats = await self.instagram_repository.get_media_user_stats(
            data.username, days=30
        )
        if isinstance(monthly_media_stats, str):
            return build_aiogram_method(
                None,
                message=TextMessage(
                    text=monthly_media_stats,
                    reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                        data.username
                    ),
                ),
                tg_object=query,
                use_edit=True,
            )

        user_reports = await self.instagram_repository.get_user_reports(data.username)

        message = TextMessage(
            text=build_tracking_stats_text(
                user_stats, weekly_media_stats, monthly_media_stats, user_info
            ),
            reply_markup=self.keyboard_repository.build_tracking_stats_keyboard(
                data.username, user_reports[0].id
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(
            None, message=message, tg_object=query, use_edit=True
        )

    async def handle_tracking_followers_following_collision(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        info = await self.instagram_repository.get_user_following_followers_collision(
            data.username
        )
        usernames = info.follow_usernames[(data.page - 1) * 15 : data.page * 15]
        message = TextMessage(
            text=build_tracking_followers_text(usernames),
            reply_markup=self.keyboard_repository.build_paginated_with_to_tracking_show(
                Action.tracking_followers_following_collision.action,
                data.username,
                len(info.follow_usernames),
                data.page,
                on_page_count=15
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(None, tg_object=query, message=message)

    async def handle_tracking_followers_following_difference(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        info = await self.instagram_repository.get_user_followers_following_difference(
            data.username
        )
        usernames = info.follow_usernames[(data.page - 1) * 15 : data.page * 15]
        message = TextMessage(
            text=build_tracking_followers_text(usernames),
            reply_markup=self.keyboard_repository.build_paginated_with_to_tracking_show(
                Action.tracking_followers_following_difference.action,
                data.username,
                len(info.follow_usernames),
                data.page,
                on_page_count=15
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(None, tg_object=query, message=message)

    async def handle_tracking_following_followers_difference(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        info = await self.instagram_repository.get_user_following_followers_difference(
            data.username
        )
        usernames = info.follow_usernames[(data.page - 1) * 15 : data.page * 15]
        message = TextMessage(
            text=build_tracking_followers_text(usernames),
            reply_markup=self.keyboard_repository.build_paginated_with_to_tracking_show(
                Action.tracking_following_followers_difference.action,
                data.username,
                len(info.follow_usernames),
                data.page,
                on_page_count=15
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(None, tg_object=query, message=message)

    async def handle_tracking_hidden_followers(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> TelegramMethod:
        info = await self.instagram_repository.get_user_hidden_followers(data.username)
        usernames = info.follow_usernames[(data.page - 1) * 15 : data.page * 15]
        message = TextMessage(
            text=build_tracking_followers_text(usernames),
            reply_markup=self.keyboard_repository.build_paginated_with_to_tracking_show(
                Action.tracking_hidden_followers.action,
                data.username,
                len(info.follow_usernames),
                data.page,
                on_page_count=15
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(None, tg_object=query, message=message)

    async def handle_report_trackings(
        self, tg_object: CallbackQuery | Message
    ) -> AsyncGenerator[TelegramMethod]:
        for tracking in await self.tracking_repository.list(
            creator_telegram_id=tg_object.from_user.id
        ):
            user_info = await self.instagram_repository.get_user_info(
                tracking.instagram_username
            )
            user_stats = await self.instagram_repository.get_user_stats(
                tracking.instagram_username
            )
            media_stats = await self.instagram_repository.get_media_user_stats(
                tracking.instagram_username
            )
            message = TextMessage(
                text=build_tracking_report_text(user_stats, media_stats, user_info),
                reply_markup=self.keyboard_repository.build_tracking_report_keyboard(
                    tracking.instagram_username
                ),
                parse_mode="MarkdownV2",
            )
            yield build_aiogram_method(tg_object.from_user.id, message)

    async def handle_report_tracking(
        self, tg_object: CallbackQuery | Message, data: TrackingReportCallback
    ) -> TelegramMethod:
        tracking = await self.tracking_repository.get(
            tg_object.from_user.id, data.username
        )
        user_info = await self.instagram_repository.get_user_info(
            tracking.instagram_username
        )
        user_stats = await self.instagram_repository.get_user_stats(
            tracking.instagram_username
        )
        media_stats = await self.instagram_repository.get_media_user_stats(
            tracking.instagram_username
        )
        if isinstance(user_info, str):
            user_info = None
        if isinstance(user_stats, str):
            user_stats = None
        if isinstance(media_stats, str):
            media_stats = None
        message = TextMessage(
            text=build_tracking_report_text(user_stats, media_stats, user_info),
            reply_markup=self.keyboard_repository.build_tracking_report_keyboard(
                tracking.instagram_username, data.report_id
            ),
            parse_mode="MarkdownV2",
        )
        return build_aiogram_method(tg_object.from_user.id, message)

    async def handle_tracking_collect_data(
        self, tg_object: CallbackQuery, data: TrackingActionCallback
    ):
        user_subscription = await self.subscription_repository.get(
            tg_object.from_user.id, data.username
        )
        if user_subscription.requests_available <= 0:
            message = TextMessage(
                text="У вас закончился баланс запросов",
                reply_markup=self.keyboard_repository.build_tracking_buy_requests_keyboard(
                    data.username
                ),
            )
            return build_aiogram_method(None, tg_object=tg_object, message=message)

        tracking_stats = await self.instagram_repository.get_user_stats_change_from_real(data.username)
        if (
            not isinstance(tracking_stats, str)
            and tracking_stats.followers_count_difference == 0
            and tracking_stats.following_count_difference == 0
            and tracking_stats.media_count_difference == 0
        ):
            message = TextMessage(
                text="Данные не изменились",
                reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                    data.username, button_text="Назад"
                ),
            )
            return build_aiogram_method(None, tg_object=tg_object, message=message)

        await self.instagram_repository.create_user_report(
            tg_object.from_user.id, data.username
        )
        await self.subscription_repository.update(
            user_subscription.id,
            requests_available=user_subscription.requests_available - 1,
        )
        message = TextMessage(
            text="Сбор данных пользователя "
            + data.username
            + " запущен. По завершению вам придет отчет. Осталось запросов: "
            + str(user_subscription.requests_available),
            reply_markup=self.keyboard_repository.build_to_tracking_show_keyboard(
                data.username, button_text="Назад"
            ),
        )
        return build_aiogram_method(None, tg_object=tg_object, message=message)
