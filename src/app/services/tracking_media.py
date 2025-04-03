import datetime as dt
from typing import Annotated
from urllib.parse import unquote_plus

from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.methods import DeleteMessage, EditMessageText, TelegramMethod

from app.repositories.instagram import InstagramRepository
from app.repositories.keyboard import KeyboardRepository
from app.repositories.tracking_media import TrackingMediaRepository
from app.schemas.action_callback import Action, TrackingActionCallback, TrackingMediaActionCallback
from app.schemas.message import MediaMessage, TextMessage
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

    async def _load_tracking_medias(self, username: str) -> list[TrackingMedia]:
        max_id = None
        tracking_medias = []
        while not (info := await self.instagram_repository.get_user_media_info(username, max_id=max_id)).last_page:
            for schema in info.items:
                model = await self.tracking_media_repository.create(
                    instagram_username=username,
                    caption_text=schema.caption_text,
                    display_uri=schema.display_uri,
                    instagram_id=schema.external_id,
                    created_at=schema.created_at,
                    updated_at=dt.datetime.now()
                )
                tracking_medias.append(model)
            max_id = info.next_max_id
        return tracking_medias

    async def _update_tracking_medias(self, username: str) -> list[TrackingMedia]:
        current_media = await self.tracking_media_repository.list(instagram_username=username, count=10000)
        current_media_instagram_id_to_id = {m.instagram_id: m.id for m in current_media}

        max_id = None
        tracking_medias = []
        while not (info := await self.instagram_repository.get_user_media_info(username, max_id=max_id)).last_page:
            for schema in info.items:
                if schema.external_id in current_media_instagram_id_to_id:
                    model = await self.tracking_media_repository.update(
                        current_media_instagram_id_to_id[schema.external_id],
                        display_uri=schema.display_uri,
                        like_count=schema.like_count,
                        comment_count=schema.comment_count
                    )
                else:
                    model = await self.tracking_media_repository.create(
                        instagram_username=username,
                        caption_text=schema.caption_text,
                        display_uri=schema.display_uri,
                        instagram_id=schema.external_id,
                        created_at=schema.created_at,
                        like_count=schema.like_count,
                        comment_count=schema.comment_count,
                        updated_at=dt.datetime.now()
                    )
                tracking_medias.append(model)
            max_id = info.next_max_id

        return tracking_medias

    async def _get_tracking_medias(self, username: str, page: int = 1) -> tuple[list[TrackingMedia], int]:
        """Return list of tracking_media for username and total count of tracking's media"""
        count = 10
        tracking_medias = await self.tracking_media_repository.list(instagram_username=username, page=page - 1, count=count)

        if not tracking_medias:
            tracking_medias = await self._load_tracking_medias(username)
            return tracking_medias[page * count:(page + 1) * count], len(tracking_medias)

        newest_media = list(sorted(tracking_medias, reverse=True, key=lambda m: m.updated_at or dt.date(year=1970, month=1, day=1)))[0]
        if (dt.datetime.now() - newest_media.updated_at).total_seconds >= 12 * 3600:
            tracking_medias = await self._update_tracking_medias(username)
            return tracking_medias[page * count:(page + 1) * count], len(tracking_medias)

        total_count = await self.tracking_media_repository.count(instagram_username=username)
        return tracking_medias, total_count

    async def handle_show_tracking_medias(self, query: CallbackQuery, data: TrackingActionCallback) -> TelegramMethod:
        models, total_count = await self._get_tracking_medias(data.username, page=data.page)
        message = TextMessage(
            text="Публикации пользователя @" + data.username,
            reply_markup=self.keyboard_repository.build_tracking_medias_list_keyboard(models, data.page, total_count),
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message)

    async def handle_tracking_media_display(self, query: CallbackQuery, data: TrackingMediaActionCallback) -> TelegramMethod:
        info = await self.instagram_repository.get_media_info(data.instagram_id)
        if info.display_uri:
            message = MediaMessage(
                caption=info.caption_text,
                document=info.display_uri,
                reply_markup=self.keyboard_repository.build_to_tracking_media_stats_keyboard(data.instagram_id, page=data.page),
                message_id=query.message.message_id
            )
        else:
            message = TextMessage(
                text=info.caption_text or "Текст и медиа отсутствуют",
                reply_markup=self.keyboard_repository.build_to_tracking_media_stats_keyboard(data.instagram_id, page=data.page),
                message_id=query.message.message_id
            )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_tracking_media_stats(self, query: CallbackQuery, data: TrackingMediaActionCallback) -> list[TelegramMethod]:
        methods = []
        if query.message.document is not None:
            methods.append(DeleteMessage(chat_id=query.from_user.id, message_id=query.message.message_id))

        model = await self.tracking_media_repository.get_by_instagram_id(data.instagram_id)
        info = await self.instagram_repository.get_media_stats(data.instagram_id)
        message = TextMessage(
            text=build_media_stats_text(info, model),
            reply_markup=self.keyboard_repository.build_to_show_tracking_media_keyboard(model.instagram_username, page=data.page),
            message_id=query.message.message_id
        )
        methods.append(build_aiogram_method(query.from_user.id, message, use_edit=not methods))

        return methods

