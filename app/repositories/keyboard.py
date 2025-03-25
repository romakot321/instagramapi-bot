from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from app.schemas.action_callback import Action, ActionCallback, TrackingActionCallback
from db.tables import Tracking


class KeyboardRepository:
    def build_main_keyboard(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(**Action.add_tracking.model_dump())
        builder.button(**Action.show_trackings.model_dump())
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_keyboard(self, username: str) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=Action.tracking_followers.text,
            callback_data=TrackingActionCallback(
                action=Action.tracking_followers.action, username=username
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

    def build_trackings_list_keyboard(self, trackings: list[Tracking]) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for tracking in trackings:
            builder.button(
                text='@' + tracking.instagram_username,
                callback_data=TrackingActionCallback(
                    action=Action.tracking_show.action, username=tracking.instagram_username
                ).pack(),
            )
        builder.adjust(1)
        return builder.as_markup()

    def build_tracking_followers_keyboard(self, tracking_username: str) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Назад",
            callback_data=TrackingActionCallback(
                action=Action.tracking_show.action, username=tracking_username
            ).pack(),
        )
        builder.adjust(1)
        return builder.as_markup()
