from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.schemas.action_callback import (
    Action,
    ActionCallback,
    TrackingActionCallback,
    TrackingMediaActionCallback,
)
from db.tables import Tracking, TrackingMedia


class KeyboardRepository:
    def build_main_keyboard(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(**Action.add_tracking.model_dump())
        builder.button(**Action.show_trackings.model_dump())
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_keyboard(
        self, username: str, subscribed: bool
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        if not subscribed:
            builder.button(
                text=Action.tracking_subscribe.text,
                callback_data=TrackingActionCallback(
                    action=Action.tracking_subscribe.action, username=username
                ).pack(),
            )
        builder.button(
            text=Action.tracking_followers.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_followers.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.show_tracking_media.text,
            callback_data=TrackingActionCallback(
                action=Action.show_tracking_media.action, username=username
            ).pack(),
        )
        builder.button(
            text=Action.tracking_stats.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_stats.action, username=username
            ).pack(),
        )
        builder.button(**Action.show_trackings.model_dump() | {"text": "К списку"})
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
        self, tracking_username: str
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Назад",
            callback_data=TrackingActionCallback(
                action=Action.tracking_show.action, username=tracking_username
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_medias_list_keyboard(
        self, tracking_medias: list[TrackingMedia]
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for media in tracking_medias:
            builder.button(
                text="@" + media.instagram_id,
                callback_data=TrackingMediaActionCallback(
                    action=Action.tracking_media_stats.action,
                    instagram_id=media.instagram_id,
                ).pack(),
            )
        builder.adjust(1)
        return builder.as_markup()

    def build_to_show_tracking_media_keyboard(
        self, tracking_username: str
    ) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Назад",
            callback_data=TrackingActionCallback(
                action=Action.show_tracking_media.action, username=tracking_username
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()
