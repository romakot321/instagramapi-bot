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
from app.services.tracking_following import TrackingFollowingService

router = Router(name=__name__)


# @router.callback_query(
        #     TrackingActionCallback.filter(
            #         F.action == Action.tracking_followings.action
            #     )
        # )
# async def tracking_followings(
        #     callback_query: CallbackQuery,
        #     callback_data: TrackingActionCallback,
        #     bot: Bot,
        #     tracking_following_service: Annotated[TrackingFollowingService, Depends(TrackingFollowingService.init)],
        # ):
#     method = await tracking_following_service.handle_tracking_followings(callback_query, callback_data)
#     await bot(method)


@router.callback_query(
    TrackingReportCallback.filter(
        F.action == Action.tracking_subscribtions.action
    )
)
async def tracking_subscribtions(
    callback_query: CallbackQuery,
    callback_data: TrackingReportCallback,
    bot: Bot,
    tracking_following_service: Annotated[TrackingFollowingService, Depends(TrackingFollowingService.init)],
):
    logger.debug(f"Listing tracking new following {callback_data=}")
    method = await tracking_following_service.handle_tracking_new_subscribes(callback_query, callback_data)
    await bot(method)


@router.callback_query(
    TrackingReportCallback.filter(
        F.action == Action.tracking_unsubscribes.action
    )
)
async def tracking_unsubscribes(
    callback_query: CallbackQuery,
    callback_data: TrackingReportCallback,
    bot: Bot,
    tracking_following_service: Annotated[TrackingFollowingService, Depends(TrackingFollowingService.init)],
):
    logger.debug(f"Listing tracking removed following {callback_data=}")
    method = await tracking_following_service.handle_tracking_new_unsubscribes(callback_query, callback_data)
    await bot(method)
