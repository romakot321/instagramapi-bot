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

from app.schemas.action_callback import Action, ActionCallback, TrackingActionCallback
from app.schemas.forms import TrackingCreateForm
from app.services.tracking import TrackingService

router = Router(name=__name__)


@router.message(
    F.text == Action.add_tracking.text
)
async def add_tracking_message(
    message: Message,
    state: FSMContext,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_form_create(message, state)
    await bot(method)


@router.callback_query(ActionCallback.filter(F.action == Action.add_tracking.action))
async def add_tracking_callback(
    callback_query: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_form_create(callback_query, state)
    await bot(method)


@router.message(
    TrackingCreateForm.typing_username, F.text
)
async def tracking_create(
    message: Message,
    state: FSMContext,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    previous_message: Message | None = None
    async for method in tracking_service.handle_create(message, state):
        msg = await bot(method)
        if previous_message is not None:
            await bot.delete_message(previous_message.chat.id, previous_message.message_id)
        previous_message = msg


@router.callback_query(
    ActionCallback.filter(
        F.action == Action.show_trackings.action
    )
)
async def show_trackings_query(
    callback_query: CallbackQuery,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_show_trackings(callback_query)
    await bot(method)


@router.message(
    F.text == Action.show_trackings.text
)
async def show_trackings_message(
    message: Message,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_show_trackings(message)
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(
        F.action == Action.tracking_show.action
    )
)
async def tracking_show(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_show(callback_query, callback_data)
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(
        F.action == Action.tracking_subscribe.action
    )
)
async def tracking_subscribe(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_subscribe(callback_query, callback_data)
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(
        F.action == Action.tracking_unsubscribe.action
    )
)
async def tracking_unsubscribe(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_unsubscribe(callback_query, callback_data)
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(
        F.action == Action.tracking_stats.action
    )
)
async def tracking_stats(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_stats(callback_query, callback_data)
    await bot(method)


@router.callback_query(
    ActionCallback.filter(
        F.action == Action.report_trackings.action
    )
)
async def report_trackings(
    callback_query: CallbackQuery,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    logger.debug("Sending reports to " + str(callback_query.from_user.id))
    methods = await tracking_service.handle_report_trackings(callback_query)
    for method in methods:
        await bot(method)
