from aiogram import Dispatcher, Bot
from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import CallbackQuery
from aiogram.types import ErrorEvent
from aiogram.types import Message
from fastapi import HTTPException
from loguru import logger
import os
import asyncio

from app.schemas.exception import ApiException


def setup_error_handlers(dispatcher: Dispatcher):
    bot_instance = Bot(os.getenv("BOT_TOKEN"))

    async def _log_error_to_admins(exc: ApiException | Exception):
        if isinstance(exc, ApiException):
            message = exc.detail() or exc.message
        else:
            message = str(exc)
        for i in range(0, len(message), 2048):
            await bot_instance.send_message(799377676, message[i:i + 2048])
            await asyncio.sleep(0.05)

    @dispatcher.error(
        ExceptionTypeFilter(ApiException), F.update.message.as_("message")
    )
    async def handle_api_error_msg(event: ErrorEvent, message: Message):
        logger.exception(event.exception)
        await message.answer("Внутреняя ошибка")
        await _log_error_to_admins(event.exception)
        return True

    @dispatcher.error(
        ExceptionTypeFilter(ApiException), F.update.callback_query.as_("callback_query")
    )
    async def handle_api_error_query(event: ErrorEvent, callback_query: CallbackQuery):
        logger.exception(event.exception)
        await bot_instance.send_message(callback_query.from_user.id, "Внутреняя ошибка")
        await _log_error_to_admins(event.exception)
        return True

    @dispatcher.error(
        ExceptionTypeFilter(HTTPException), F.update.message.as_("message")
    )
    async def handle_http_error_msg(event: ErrorEvent, message: Message):
        logger.exception(event.exception)
        match event.exception.status_code:
            case 404:
                await message.answer("Не найдено")
            case 422:
                await message.answer("Неверный QR-Код")
        return True

    @dispatcher.error(
        ExceptionTypeFilter(HTTPException), F.update.callback_query.as_("query")
    )
    async def handle_http_error_callback(
            event: ErrorEvent,
            query: CallbackQuery
    ):
        logger.exception(event.exception)
        match event.exception.status_code:
            case 404:
                await query.answer("Не найдено")
            case 422:
                await query.answer("Неверный QR-Код")
        return True

    @dispatcher.error(
        ExceptionTypeFilter(TelegramBadRequest), F.update.callback_query.as_("query")
    )
    async def handle_tg_bad_request(
            event: ErrorEvent,
            query: CallbackQuery
    ):
        logger.exception(event.exception)
        proper_messages = ['message is not modified', 'canceled by new editMessageMedia request', 'message to delete not found', 'message to edit not found', 'bot was blocked by the user']
        if not any(msg in event.exception.message for msg in proper_messages):
            logger.exception(event.exception)
            await _log_error_to_admins(event.exception)
            return False
        try:
            await query.answer()
        except TelegramBadRequest:
            pass
        return True

    @dispatcher.error(
        ExceptionTypeFilter(Exception), F.update.callback_query.as_("query")
    )
    async def handle_internal_exception(
            event: ErrorEvent,
            query: CallbackQuery
    ):
        logger.exception(event.exception)
        await query.answer("Внутреняя ошибка")
        await _log_error_to_admins(event.exception)
        return True
