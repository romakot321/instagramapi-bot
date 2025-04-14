import os
from typing import Annotated
from aiohttp import ClientSession
from loguru import logger

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram3_di import Depends

from app.schemas.action_callback import Action, ActionCallback, TrackingActionCallback
from app.schemas.forms import TrackingCreateForm
from app.services.tracking import TrackingService

router = Router(name=__name__)


@router.message(Command("report"))
async def get_user_reports(
    message: Message,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    logger.debug("Sending reports to " + str(message.from_user.id))
    async for method in tracking_service.handle_report_trackings(message):
        await bot(method)


@router.message(Command("run"))
async def create_tracking_report(
    message: Message,
    command: CommandObject,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    if not command.args:
        return
    tracking_username = command.args

    async with ClientSession(base_url=os.getenv("INSTAGRAM_API_URL")) as session:
        resp = await session.post(f"/api/user/{tracking_username}/report", json={"webhook_url": f"http://instagrambot_app/api/user/{message.from_user.id}/report"})
        if resp.status != 202:
            raise ValueError("Failed to send create report request: " + await resp.text())

    await message.answer(f"Сбор данных пользователя {tracking_username} запущен")


@router.message(F.text == Action.add_tracking.text)
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


@router.message(F.text.not_in([i.text for i in Action]))
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
            await bot.delete_message(
                previous_message.chat.id, previous_message.message_id
            )
        previous_message = msg


@router.callback_query(ActionCallback.filter(F.action == Action.show_trackings.action))
async def show_trackings_query(
    callback_query: CallbackQuery,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_show_trackings(callback_query)
    await bot(method)


@router.message(F.text == Action.show_trackings.text)
async def show_trackings_message(
    message: Message,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_show_trackings(message)
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(F.action == Action.tracking_show.action)
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
    TrackingActionCallback.filter(F.action == Action.tracking_subscribe.action)
)
async def tracking_subscribe(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_subscribe(
        callback_query, callback_data
    )
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(F.action == Action.tracking_unsubscribe.action)
)
async def tracking_unsubscribe(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_unsubscribe(
        callback_query, callback_data
    )
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(F.action == Action.tracking_stats.action)
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
    TrackingActionCallback.filter(
        F.action == Action.tracking_followers_following_collision.action
    )
)
async def tracking_followers_following_collision(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_followers_following_collision(
        callback_query, callback_data
    )
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(F.action == Action.tracking_settings.action)
)
async def tracking_settings(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_settings(callback_query, callback_data)
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(
        F.action == Action.tracking_followers_following_difference.action
    )
)
async def tracking_followers_following_difference(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_followers_following_difference(
        callback_query, callback_data
    )
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(
        F.action == Action.tracking_following_followers_difference.action
    )
)
async def tracking_following_followers_difference(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_following_followers_difference(
        callback_query, callback_data
    )
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(F.action == Action.tracking_hidden_followers.action)
)
async def tracking_hidden_followers(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    method = await tracking_service.handle_tracking_hidden_followers(
        callback_query, callback_data
    )
    await bot(method)


@router.callback_query(
    ActionCallback.filter(F.action == Action.report_trackings.action)
)
async def report_trackings(
    callback_query: CallbackQuery,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    logger.debug("Sending reports to " + str(callback_query.from_user.id))
    async for method in tracking_service.handle_report_trackings(callback_query):
        await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(F.action == Action.report_trackings.action)
)
async def report_tracking(
    callback_query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    tracking_service: Annotated[TrackingService, Depends(TrackingService.init)],
):
    logger.debug(
        f"Sending report {callback_data.username} to "
        + str(callback_query.from_user.id)
    )
    method = await tracking_service.handle_report_tracking(callback_query, callback_data)
    await bot(method)
