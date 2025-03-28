import datetime as dt
from typing import Annotated

from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.methods import EditMessageText, TelegramMethod

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.tracking_media import TrackingMediaRepository
from app.schemas.action_callback import Action, TrackingActionCallback, TrackingMediaActionCallback
from app.schemas.message import TextMessage
from app.schemas.texts import build_media_stats_text
from app.services.utils import build_aiogram_method
from db.tables import TrackingMedia


class TrackingMediaService:
    def __init__(
        self,
        tracking_media_repository: TrackingMediaRepository,
        instagram_repository: InstagramRepository,
        keyboard_repository: KeyboardRepository,
    ):
        self.tracking_media_repository = tracking_media_repository
        self.instagram_repository = instagram_repository
        self.keyboard_repository = keyboard_repository

    @classmethod
    def init(
        cls,
        tracking_media_repository: Annotated[TrackingMediaRepository, Depends(TrackingMediaRepository.depend)],
        instagram_repository: Annotated[
            InstagramRepository, Depends(InstagramRepository)
        ],
        keyboard_repository: Annotated[KeyboardRepository, Depends(KeyboardRepository)],
    ):
        return cls(
            tracking_media_repository=tracking_media_repository,
            instagram_repository=instagram_repository,
            keyboard_repository=keyboard_repository,
        )

    async def _load_tracking_medias(self, username: str, creator_telegram_id: int, page: int = 0) -> list[TrackingMedia]:
        count = 10
        tracking_medias = await self.tracking_media_repository.list(instagram_username=username, page=page, count=count)
        if tracking_medias:
            return tracking_medias

        max_id = None
        while not (info := await self.instagram_repository.get_user_media_info(username, max_id=max_id)).last_page:
            for schema in info.items:
                model = await self.tracking_media_repository.create(
                    creator_telegram_id=creator_telegram_id,
                    instagram_username=username,
                    caption_text=schema.caption_text,
                    display_uri=schema.display_uri,
                    instagram_id=schema.external_id
                )
                tracking_medias.append(model)
            max_id = info.next_max_id
        return tracking_medias[page * count:(page + 1) * count]

    async def handle_show_tracking_medias(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        models = await self._load_tracking_medias(data.username, query.from_user.id, page=data.page)
        message = TextMessage(
            text="Публикации пользователя @" + data.username,
            reply_markup=self.keyboard_repository.build_tracking_medias_list_keyboard(models),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_tracking_media_stats(self, query: CallbackQuery, data: TrackingMediaActionCallback) -> TelegramMethod:
        model = await self.tracking_media_repository.get_by_instagram_id(data.instagram_id)
        info = await self.instagram_repository.get_media_stats(data.instagram_id)
        message = TextMessage(
            text=build_media_stats_text(info, model),
            reply_markup=self.keyboard_repository.build_to_show_tracking_media_keyboard(model.instagram_username),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

