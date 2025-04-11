from aiogram import Dispatcher
from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import CallbackQuery
from aiogram.types import ErrorEvent
from aiogram.types import Message
from fastapi import HTTPException
from loguru import logger

from app.schemas.exception import ApiException
from app import bot_instance


def setup_error_handlers(dispatcher: Dispatcher):
    @dispatcher.error(
        ExceptionTypeFilter(ApiException), F.update.message.as_("message")
    )
    async def handle_api_error_msg(event: ErrorEvent, message: Message):
        logger.exception(event.exception)
        await message.answer("Внутреняя ошибка")
        await bot_instance.send_message(799377676, event.exception.detail() or event.exception.message)
        return True

    @dispatcher.error(
        ExceptionTypeFilter(ApiException), F.update.callback_query.as_("callback_query")
    )
    async def handle_api_error_query(event: ErrorEvent, callback_query: CallbackQuery):
        logger.exception(event.exception)
        await bot_instance.send_message(callback_query.from_user.id, "Внутреняя ошибка")
        await bot_instance.send_message(799377676, event.exception.detail() or event.exception.message)
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
        return True
