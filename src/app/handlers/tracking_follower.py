from typing import Annotated
from loguru import logger

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram3_di import Depends

from app.schemas.action_callback import Action, ActionCallback, TrackingActionCallback, TrackingReportCallback
from app.schemas.forms import TrackingCreateForm
from app.services.tracking_follower import TrackingFollowerService

router = Router(name=__name__)


@router.callback_query(
    TrackingActionCallback.filter(
        F.action == Action.tracking_followers.action
    )
)
async def tracking_followers(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_follower_service: Annotated[TrackingFollowerService, Depends(TrackingFollowerService.init)],
):
    method = await tracking_follower_service.handle_tracking_followers(callback_query, callback_data)
    await bot(method)


@router.callback_query(
    TrackingReportCallback.filter(
        F.action == Action.tracking_new_subscribers.action
    )
)
async def tracking_new_subscribes(
    callback_query: CallbackQuery,
    callback_data: TrackingReportCallback,
    bot: Bot,
    tracking_follower_service: Annotated[TrackingFollowerService, Depends(TrackingFollowerService.init)],
):
    logger.debug(f"Listing tracking new followers {callback_data=}")
    method = await tracking_follower_service.handle_tracking_new_subscribes(callback_query, callback_data)
    await bot(method)


@router.callback_query(
    TrackingReportCallback.filter(
        F.action == Action.tracking_new_unsubscribed.action
    )
)
async def tracking_new_unsubscribes(
    callback_query: CallbackQuery,
    callback_data: TrackingReportCallback,
    bot: Bot,
    tracking_follower_service: Annotated[TrackingFollowerService, Depends(TrackingFollowerService.init)],
):
    logger.debug(f"Listing tracking removed followers {callback_data=}")
    method = await tracking_follower_service.handle_tracking_new_unsubscribes(callback_query, callback_data)
    await bot(method)
