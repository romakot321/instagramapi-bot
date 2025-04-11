from typing import Annotated
from loguru import logger

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram3_di import Depends

from app.schemas.action_callback import Action
from app.services.support import SupportService

router = Router(name=__name__)


@router.message(
    F.text == Action.support_menu.text
)
async def support_menu(
    message: Message,
    bot: Bot,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.handle_support_menu(message)
    await bot(method)
