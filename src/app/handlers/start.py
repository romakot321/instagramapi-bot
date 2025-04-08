from typing import Annotated

from aiogram import F, Router
from aiogram import Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram3_di import Depends

from app.schemas.action_callback import Action, ActionCallback
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


@router.callback_query(ActionCallback.filter(F.action == Action.main_menu.action))
async def main_menu(
    callback_query: CallbackQuery,
    bot: Bot,
    user_service: Annotated[UserService, Depends(UserService.init)],
):
    method = await user_service.handle_user_start(callback_query)
    await bot(method)


@router.callback_query(ActionCallback.filter(F.action == Action.delete_message.action))
async def delete_message(callback_query: CallbackQuery, bot: Bot):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)


# @router.message(F.text.not_in([i.text for i in Action]) and StateFilter(None))
# async def unknown_command(message: Message):
#     await message.answer("Неизвестная команда")
