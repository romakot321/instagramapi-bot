import datetime as dt
import json
import mimetypes
from loguru import logger
from typing import Annotated, AsyncGenerator
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
from app.schemas.action_callback import (
    Action,
    TrackingActionCallback,
    TrackingMediaActionCallback,
)
from app.schemas.message import (
    MediaGroupMessage,
    MediaMessage,
    PhotoMessage,
    TextMessage,
    VideoMessage,
)
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
        tracking_media_repository: Annotated[
            TrackingMediaRepository, Depends(TrackingMediaRepository.depend)
        ],
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
        while True:
            info = await self.instagram_repository.get_user_media_info(
                username, count=12, max_id=max_id
            )
            logger.debug("Load tracking response: " + str(info))
            for schema in info.items:
                model = await self.tracking_media_repository.create(
                    instagram_username=username,
                    caption_text=schema.caption_text,
                    display_uri=schema.display_uri,
                    instagram_id=schema.external_id,
                    created_at=schema.created_at,
                    like_count=schema.like_count,
                    comment_count=schema.comment_count,
                    updated_at=dt.datetime.now(),
                )
                tracking_medias.append(model)
            if info.last_page:
                break
            max_id = info.next_max_id
        return tracking_medias

    async def _update_tracking_medias(self, username: str) -> list[TrackingMedia]:
        current_media = await self.tracking_media_repository.list(
            instagram_username=username, count=10000
        )
        current_media_instagram_id_to_id = {m.instagram_id: m.id for m in current_media}

        max_id = None
        tracking_medias = []
        while not (
            info := await self.instagram_repository.get_user_media_info(
                username, count=12, max_id=max_id
            )
        ).last_page:
            for schema in info.items:
                if schema.external_id in current_media_instagram_id_to_id:
                    model = await self.tracking_media_repository.update(
                        current_media_instagram_id_to_id[schema.external_id],
                        display_uri=schema.display_uri,
                        like_count=schema.like_count,
                        comment_count=schema.comment_count,
                        updated_at=dt.datetime.now(),
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
                        updated_at=dt.datetime.now(),
                    )
                tracking_medias.append(model)
            max_id = info.next_max_id

        return tracking_medias

    async def _get_tracking_medias(
        self, username: str, page: int = 1, update: bool = False
    ) -> tuple[list[TrackingMedia], int] | None:
        """Return list of tracking_media for username and total count of tracking's media"""
        count = 10
        tracking_medias = await self.tracking_media_repository.list(
            instagram_username=username, page=page - 1, count=count
        )

        if not tracking_medias and not update:
            return None
        if not tracking_medias:
            tracking_medias = await self._load_tracking_medias(username)
            logger.debug("Loadded medias: " + str(tracking_medias))
            logger.debug(f"Paginated(page: {page}, count: {count}): " + str(tracking_medias[(page - 1) * count : page * count]))
            return tracking_medias[(page - 1) * count : page * count], len(
                tracking_medias
            )
        total_count = await self.tracking_media_repository.count(
            instagram_username=username
        )

        newest_media = list(
            sorted(
                tracking_medias,
                reverse=True,
                key=lambda m: m.updated_at or dt.date(year=1970, month=1, day=1),
            )
        )[0]
        if (dt.datetime.now() - newest_media.updated_at).total_seconds() >= 12 * 3600:
            if not update:
                return None
            tracking_info = await self.instagram_repository.get_user_info(username)
            if tracking_info.media_count != total_count:
                tracking_medias = await self._update_tracking_medias(username)
                return tracking_medias[(page - 1) * count : page * count], len(
                    tracking_medias
                )

        return tracking_medias, total_count

    async def handle_show_tracking_medias(
        self, query: CallbackQuery, data: TrackingActionCallback
    ) -> AsyncGenerator[TelegramMethod]:
        use_edit = True
        if (
            query.message.document is not None
            or query.message.photo is not None
            or query.message.video is not None
        ):
            yield DeleteMessage(
                chat_id=query.from_user.id, message_id=query.message.message_id
            )
            use_edit = False

        medias = await self._get_tracking_medias(data.username, page=data.page)
        if medias is None:
            yield build_aiogram_method(
                None,
                tg_object=query,
                message=TextMessage(text="Загружаем посты..."),
                use_edit=use_edit,
            )
            models, total_count = await self._get_tracking_medias(
                data.username, page=data.page, update=True
            )
        else:
            models, total_count = medias
        message = TextMessage(
            text="Публикации пользователя " + data.username if total_count > 0 else "Публикаций нет",
            reply_markup=self.keyboard_repository.build_tracking_medias_list_keyboard(
                models, data.page, total_count
            ),
            message_id=query.message.message_id,
        )
        yield build_aiogram_method(query.from_user.id, message, use_edit=use_edit)

    async def handle_tracking_media_stats(
        self, query: CallbackQuery, data: TrackingMediaActionCallback
    ) -> list[TelegramMethod]:
        methods = []
        use_edit = True

        model = await self.tracking_media_repository.get_by_instagram_id(
            data.instagram_id
        )
        info = await self.instagram_repository.get_media_info(data.instagram_id)
        stats = await self.instagram_repository.get_media_stats(data.instagram_id)
        if info.display_uri is None:
            message = TextMessage(
                text=build_media_stats_text(stats, model),
                reply_markup=self.keyboard_repository.build_tracking_media_keyboard(
                    model, page=data.page
                ),
                parse_mode="MarkdownV2",
            )
        elif info.display_uri.startswith("[") and info.display_uri.endswith("]"):
            urls = json.loads(info.display_uri)
            message = PhotoMessage(
                caption=build_media_stats_text(stats, model),
                reply_markup=self.keyboard_repository.build_tracking_media_paginated_keyboard(
                    model, len(urls), data.page, data.media_page
                ),
                photo=urls[data.media_page - 1],
                parse_mode="MarkdownV2",
            )
        elif mimetypes.guess_type(info.display_uri)[0] is None:
            message = TextMessage(
                text=build_media_stats_text(stats, model),
                reply_markup=self.keyboard_repository.build_tracking_media_keyboard(model, page=data.page),
                parse_mode="MarkdownV2"
            )
        elif mimetypes.guess_type(info.display_uri)[0].startswith("video/"):
            message = VideoMessage(
                caption=build_media_stats_text(stats, model),
                reply_markup=self.keyboard_repository.build_tracking_media_keyboard(
                    model, page=data.page
                ),
                video=info.display_uri,
                parse_mode="MarkdownV2",
            )
        elif mimetypes.guess_type(info.display_uri)[0].startswith("image/"):
            message = PhotoMessage(
                caption=build_media_stats_text(stats, model),
                reply_markup=self.keyboard_repository.build_tracking_media_keyboard(
                    model, page=data.page
                ),
                photo=info.display_uri,
                parse_mode="MarkdownV2",
            )
        else:
            message = TextMessage(
                text=build_media_stats_text(stats, model),
                reply_markup=self.keyboard_repository.build_tracking_media_keyboard(
                    model, page=data.page
                ),
                parse_mode="MarkdownV2",
            )

        methods.append(build_aiogram_method(None, message=message, tg_object=query, use_edit=use_edit))

        return methods
