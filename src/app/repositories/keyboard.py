from aiogram import types
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import humanize
import datetime as dt
import math
import os
from urllib.parse import urlparse

from app.schemas.action_callback import (
    Action,
    ActionCallback,
    PaginatedActionCallback,
    SubscriptionActionCallback,
    TrackingActionCallback,
    TrackingMediaActionCallback,
)
from app.schemas.texts import media_display_url_to_emoji
from db.tables import Tariff, Tracking, TrackingMedia

BOT_WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL", "")
humanize.i18n.activate("RU_ru")


class KeyboardRepository:
    def build_main_keyboard(self) -> types.ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        builder.button(**Action.add_tracking.model_dump())
        builder.button(**Action.show_trackings.model_dump())
        builder.button(**Action.subscription_menu.model_dump())
        builder.button(**Action.support_menu.model_dump())
        builder.adjust(1)
        markup = builder.as_markup()
        markup.resize_keyboard = True
        return markup

    def build_paywall_keyboard(
        self, tracking_username: str | None = None, tariff_id: int | None = None
    ) -> types.InlineKeyboardMarkup:
        url = "https://" + urlparse(BOT_WEBHOOK_URL).netloc + "/paywall"
        if tracking_username and tariff_id:
            url += (
                "?tracking_username="
                + tracking_username
                + "&tariff_id="
                + str(tariff_id)
            )

        builder = InlineKeyboardBuilder()
        builder.button(
            text=Action.subscription_add.text,
            web_app=types.WebAppInfo(url=url),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_paywall_big_tracking_keyboard(
        self, tracking_username: str
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=Action.subscription_add.text,
            web_app=types.WebAppInfo(
                url="https://"
                + urlparse(BOT_WEBHOOK_URL).netloc
                + "/paywall/bigTracking?username="
                + tracking_username
            ),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_to_add_tracking_keyboard(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(**Action.add_tracking.model_dump())
        return builder.as_markup()

    def build_to_trackings_max_buy_keyboard(
        self, tracking_username: str
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Купить доп. отслеживание",
            callback_data=SubscriptionActionCallback(
                action=Action.subscription_add.action,
                t_id=-1,
                ig_u=tracking_username
            )
        )
        builder.button(
            text="Назад",
            callback_data=TrackingActionCallback(
                action=Action.tracking_show.action, username=tracking_username
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_to_paywall_big_tracking_keyboard(
        self, tracking_username: str
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Оплатить доступ",
            callback_data=TrackingActionCallback(
                action=Action.subscription_add.action, username=tracking_username
            ).pack(),
        )
        builder.button(
            text="Назад",
            callback_data=TrackingActionCallback(
                action=Action.tracking_show.action, username=tracking_username
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_to_paywall_keyboard(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(**Action.subscription_add.model_dump())
        builder.adjust(1)
        return builder.as_markup()

    def build_subscription_menu_keyboard(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(**Action.subscription_cancel.model_dump())
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_settings_keyboard(
        self, username: str, tarrifs: list[Tariff]
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for tariff in tarrifs:
            builder.button(
                text="Отслеживать статистику раз в "
                + humanize.naturaldelta(
                    dt.timedelta(seconds=int(tariff.tracking_report_interval))
                ),
                callback_data=SubscriptionActionCallback(
                    action=Action.tracking_report_interval.action,
                    ig_u=username,
                    t_id=tariff.id,
                ),
            )
        builder.button(
            text="Назад",
            callback_data=TrackingActionCallback(
                action=Action.tracking_show.action, username=username
            ),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_keyboard(
        self, username: str, subscribed: bool
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text=Action.tracking_stats.text,
                callback_data=TrackingActionCallback(
                    action=Action.tracking_stats.action, username=username
                ).pack(),
            )
        )
        if subscribed:
            builder.row(
                types.InlineKeyboardButton(
                    text=Action.show_tracking_media.text,
                    callback_data=TrackingActionCallback(
                        action=Action.show_tracking_media.action, username=username
                    ).pack(),
                )
            )
            builder.row(
                types.InlineKeyboardButton(
                    text=Action.tracking_followers_following_collision.text,
                    callback_data=TrackingActionCallback(
                        action=Action.tracking_followers_following_collision.action,
                        username=username,
                    ).pack(),
                )
            )
            builder.row(
                types.InlineKeyboardButton(
                    text=Action.tracking_followers_following_difference.text,
                    callback_data=TrackingActionCallback(
                        action=Action.tracking_followers_following_difference.action,
                        username=username,
                    ).pack(),
                ),
                types.InlineKeyboardButton(
                    text=Action.tracking_following_followers_difference.text,
                    callback_data=TrackingActionCallback(
                        action=Action.tracking_following_followers_difference.action,
                        username=username,
                    ).pack(),
                ),
            )
            builder.row(
                types.InlineKeyboardButton(
                    text=Action.tracking_hidden_followers.text,
                    callback_data=TrackingActionCallback(
                        action=Action.tracking_hidden_followers.action, username=username
                    ).pack(),
                )
            )
            builder.row(
                types.InlineKeyboardButton(
                    text=Action.tracking_settings.text,
                    callback_data=TrackingActionCallback(
                        action=Action.tracking_settings.action, username=username
                    ).pack(),
                )
            )
            builder.row(
                types.InlineKeyboardButton(
                    text=Action.tracking_unsubscribe.text,
                    callback_data=TrackingActionCallback(
                        action=Action.tracking_unsubscribe.action, username=username
                    ).pack(),
                )
            )
        else:
            builder.row(
                types.InlineKeyboardButton(
                    text=Action.tracking_subscribe.text,
                    callback_data=TrackingActionCallback(
                        action=Action.tracking_subscribe.action, username=username
                    ).pack(),
                )
            )
        return builder.as_markup()

    def build_tracking_show_full_keyboard(self, tracking_username: str) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Начать следить за пользователем",
            callback_data=SubscriptionActionCallback(
                action=Action.subscription_add.action,
                t_id=-1,
                ig_u=tracking_username
            )
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_trackings_list_keyboard(
        self, trackings: list[Tracking]
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for tracking in trackings:
            builder.button(
                text="@" + tracking.instagram_username,
                callback_data=TrackingActionCallback(
                    action=Action.tracking_show.action,
                    username=tracking.instagram_username,
                ).pack(),
            )
        builder.adjust(1)
        return builder.as_markup()

    def build_to_tracking_show_keyboard(
        self, tracking_username: str, button_text: str | None = None
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Назад" if button_text is None else button_text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_show.action, username=tracking_username
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_media_paginated_keyboard(self, tracking_media: TrackingMedia, total_count: int, page: int, media_page: int):
        builder = InlineKeyboardBuilder()
        if total_count > 1:
            builder.row(
                *self.paginate_row(
                    total_count,
                    media_page,
                    TrackingMediaActionCallback(
                        action=Action.tracking_media_stats.action,
                        instagram_id=tracking_media.instagram_id
                    ),
                    on_page_count=1,
                    page_key="media_page"
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=TrackingActionCallback(
                    action=Action.show_tracking_media.action,
                    username=tracking_media.instagram_username,
                    page=page,
                ).pack(),
            )
        )
        return builder.as_markup()

    def build_tracking_media_keyboard(
        self,
        tracking_media: TrackingMedia,
        page: int = 0
    ):
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Назад",
            callback_data=TrackingActionCallback(
                action=Action.show_tracking_media.action,
                username=tracking_media.instagram_username,
                page=page,
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_to_tracking_media_stats_keyboard(
        self, tracking_media_instagram_id: str, page: int = 0
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=TrackingMediaActionCallback(
                    action=Action.tracking_media_stats.action,
                    instagram_id=tracking_media_instagram_id,
                    page=page,
                ).pack(),
            )
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_medias_list_keyboard(
        self,
        tracking_medias: list[TrackingMedia],
        current_page: int,
        total_media_count: int,
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for media in tracking_medias:
            emoji = media_display_url_to_emoji(media.display_uri)
            builder.row(
                types.InlineKeyboardButton(
                    text=emoji
                    + " "
                    + media.created_at.strftime("%d.%m.%Y %H:%M")
                    + f"  {media.like_count} ❤️ {media.comment_count} 💬",
                    callback_data=TrackingMediaActionCallback(
                        action=Action.tracking_media_stats.action,
                        instagram_id=media.instagram_id,
                        page=current_page,
                    ).pack(),
                )
            )
        if total_media_count > 10:
            builder.row(
                *self.paginate_row(
                    total_media_count,
                    current_page,
                    TrackingActionCallback(
                        action=Action.show_tracking_media.action,
                        username=tracking_medias[0].instagram_username,
                    ),
                    on_page_count=10,
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=TrackingActionCallback(
                    action=Action.tracking_show.action,
                    username=tracking_medias[0].instagram_username,
                ).pack(),
            )
        )
        return builder.as_markup()

    def build_to_show_tracking_media_keyboard(
        self, tracking_username: str, page: int = 1
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Назад",
            callback_data=TrackingActionCallback(
                action=Action.show_tracking_media.action,
                username=tracking_username,
                page=page,
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_to_trackings_list_keyboard(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(**Action.show_trackings.model_dump())
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_stats_keyboard(self, username: str) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=Action.tracking_new_subscribers.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_new_subscribers.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.tracking_new_unsubscribed.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_new_unsubscribed.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.tracking_subscribtions.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_subscribtions.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.tracking_unsubscribes.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_unsubscribes.action, username=username
            ).pack(),
        )
        builder.row(
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=TrackingActionCallback(
                    action=Action.tracking_show.action, username=tracking_username
                ).pack(),
            )
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_report_keyboard(
        self, username: str
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=Action.tracking_new_subscribers.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_new_subscribers.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.tracking_new_unsubscribed.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_new_unsubscribed.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.tracking_subscribtions.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_subscribtions.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.tracking_unsubscribes.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_unsubscribes.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.tracking_stats.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_stats.action, username=username
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_new_unsubscribes_keyboard(
        self, username: str, total_count: int, current_page, on_page_count: int = 10
    ):
        builder = InlineKeyboardBuilder()
        if total_count > 10:
            builder.row(
                *self.paginate_row(
                    total_count,
                    current_page,
                    TrackingActionCallback(
                        action=Action.tracking_new_unsubscribed.action,
                        username=username,
                    ),
                    on_page_count,
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text=Action.delete_message.text,
                callback_data=ActionCallback(
                    action=Action.delete_message.action
                ).pack(),
            )
        )
        return builder.as_markup()

    def build_tracking_subscribtions_keyboard(
        self, username: str, total_count: int, current_page, on_page_count: int = 10
    ):
        builder = InlineKeyboardBuilder()
        if total_count > 10:
            builder.row(
                *self.paginate_row(
                    total_count,
                    current_page,
                    TrackingActionCallback(
                        action=Action.tracking_subscribtions.action,
                        username=username,
                    ),
                    on_page_count,
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text=Action.delete_message.text,
                callback_data=ActionCallback(
                    action=Action.delete_message.action
                ).pack(),
            )
        )
        return builder.as_markup()

    def build_tracking_unsubscribes_keyboard(
        self, username: str, total_count: int, current_page, on_page_count: int = 10
    ):
        builder = InlineKeyboardBuilder()
        if total_count > 10:
            builder.row(
                *self.paginate_row(
                    total_count,
                    current_page,
                    TrackingActionCallback(
                        action=Action.tracking_unsubscribes.action,
                        username=username,
                    ),
                    on_page_count,
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text=Action.delete_message.text,
                callback_data=ActionCallback(
                    action=Action.delete_message.action
                ).pack(),
            )
        )
        return builder.as_markup()

    def build_tracking_new_subscribes_keyboard(
        self, username: str, total_count: int, current_page, on_page_count: int = 10
    ):
        builder = InlineKeyboardBuilder()
        if total_count > 10:
            builder.row(
                *self.paginate_row(
                    total_count,
                    current_page,
                    TrackingActionCallback(
                        action=Action.tracking_new_subscribers.action,
                        username=username,
                    ),
                    on_page_count,
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text=Action.delete_message.text,
                callback_data=ActionCallback(
                    action=Action.delete_message.action
                ).pack(),
            )
        )
        return builder.as_markup()

    def build_paginated_with_to_tracking_show(
        self,
        action: str,
        tracking_username: str,
        total_count: int,
        current_page: int,
        on_page_count: int = 10,
    ):
        builder = InlineKeyboardBuilder()
        if total_count > 10:
            builder.row(
                *self.paginate_row(
                    total_count,
                    current_page,
                    TrackingActionCallback(
                        action=action,
                        username=tracking_username,
                    ),
                    on_page_count,
                )
            )
        builder.row(
            types.InlineKeyboardButton(
                text="Назад",
                callback_data=TrackingActionCallback(
                    action=Action.tracking_show.action, username=tracking_username
                ).pack(),
            )
        )
        return builder.as_markup()

    def paginate_row(
        self,
        total_count: int,
        current_page: int,
        callback_data: PaginatedActionCallback,
        on_page_count: int = 50,
        page_key: str = "page"
    ) -> list[types.InlineKeyboardButton]:
        buttons = []
        total_pages = math.ceil(total_count / on_page_count)
        if current_page > 1:
            buttons.append(
                types.InlineKeyboardButton(
                    text="⬅️",
                    callback_data=callback_data.replace(**{page_key: current_page - 1}).pack(),
                )
            )
        buttons.append(
            types.InlineKeyboardButton(
                text=f"{current_page} / {total_pages}", callback_data="a"
            )
        )
        if current_page < total_pages:
            buttons.append(
                types.InlineKeyboardButton(
                    text="➡️",
                    callback_data=callback_data.replace(**{page_key: current_page + 1}).pack(),
                )
            )
        return buttons
