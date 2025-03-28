from typing import Annotated

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram3_di import Depends

from app.schemas.action_callback import Action, ActionCallback, TrackingActionCallback, TrackingMediaActionCallback
from app.services.tracking_media import TrackingMediaService

router = Router(name=__name__)


@router.callback_query(
    TrackingActionCallback.filter(
        F.action == Action.show_tracking_media.action
    )
)
async def show_tracking_media(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_media_service: Annotated[TrackingMediaService, Depends(TrackingMediaService.init)],
):
    for method in (await tracking_media_service.handle_show_tracking_medias(callback_query, callback_data)):
        await bot(method)


@router.callback_query(
    TrackingMediaActionCallback.filter(
        F.action == Action.tracking_media_stats.action
    )
)
async def tracking_media_stats(
    callback_query: CallbackQuery,
    callback_data: TrackingMediaActionCallback,
    bot: Bot,
    tracking_media_service: Annotated[TrackingMediaService, Depends(TrackingMediaService.init)],
):
    method = await tracking_media_service.handle_tracking_media_stats(callback_query, callback_data)
    await bot(method)

