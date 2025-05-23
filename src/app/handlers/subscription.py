from typing import Annotated

from aiogram import F, Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram3_di import Depends

from app.schemas.action_callback import (
    Action,
    ActionCallback,
    SubscriptionActionCallback,
    TrackingActionCallback,
)
from app.services.subscription import SubscriptionService

router = Router(name=__name__)


@router.callback_query(
    ActionCallback.filter(F.action == Action.subscription_menu.action)
)
async def subscription_menu_query(
    query: CallbackQuery,
    bot: Bot,
    subscription_service: Annotated[
        SubscriptionService, Depends(SubscriptionService.init)
    ],
):
    method = await subscription_service.handle_subscription_menu(query)
    await bot(method)


@router.callback_query(
    ActionCallback.filter(F.action == Action.subscription_cancel.action)
)
async def subscription_cancel(
    query: CallbackQuery,
    bot: Bot,
    subscription_service: Annotated[SubscriptionService, Depends(SubscriptionService.init)]
):
    method = await subscription_service.handle_subscription_cancel(query)
    await bot(method)


@router.message(F.text == Action.subscription_menu.text)
async def subscription_menu_message(
    message: Message,
    bot: Bot,
    subscription_service: Annotated[
        SubscriptionService, Depends(SubscriptionService.init)
    ],
):
    method = await subscription_service.handle_subscription_menu(message)
    await bot(method)


@router.callback_query(
    TrackingActionCallback.filter(F.action == Action.subscription_add.action)
)
async def subscription_add_big_tracking(
    query: CallbackQuery,
    callback_data: TrackingActionCallback,
    bot: Bot,
    subscription_service: Annotated[
        SubscriptionService, Depends(SubscriptionService.init)
    ],
):
    method = await subscription_service.handle_subscription_add_big_tracking(
        query, callback_data
    )
    await bot(method)


@router.callback_query(
    SubscriptionActionCallback.filter(
        F.action == Action.tracking_report_interval.action
    )
)
async def tracking_report_interval(
    query: CallbackQuery,
    callback_data: SubscriptionActionCallback,
    bot: Bot,
    subscription_service: Annotated[
        SubscriptionService, Depends(SubscriptionService.init)
    ],
):
    method = await subscription_service.handle_subscription_upgrade(
        query, callback_data
    )
    await bot(method)


@router.callback_query(
    SubscriptionActionCallback.filter(F.action == Action.subscription_add.action)
)
async def subscription_add(
    query: CallbackQuery,
    callback_data: SubscriptionActionCallback,
    bot: Bot,
    subscription_service: Annotated[
        SubscriptionService, Depends(SubscriptionService.init)
    ],
):
    for method in (await subscription_service.handle_subscription_add(query, callback_data)):
        await bot(method)


@router.callback_query(
    SubscriptionActionCallback.filter(F.action == Action.subscription_created.action)
)
async def subscription_created(
    query: CallbackQuery,
    callback_data: SubscriptionActionCallback,
    bot: Bot,
    subscription_service: Annotated[
        SubscriptionService, Depends(SubscriptionService.init)
    ],
):
    method = await subscription_service.handle_subscription_add_created(
        query, callback_data
    )
    await bot(method)
