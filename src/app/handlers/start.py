from typing import Annotated

from aiogram import Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram3_di import Depends

from app.services.user import UserService

router = Router(name=__name__)


@router.message(CommandStart())
async def start_command(
    message: Message,
    bot: Bot,
    user_service: Annotated[UserService, Depends(UserService.init)],
):
    method = await user_service.handle_user_start(message)
    await bot(method)
