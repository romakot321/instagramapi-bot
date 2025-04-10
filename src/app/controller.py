from fastapi import Depends
from aiogram.filters.callback_data import CallbackData
import app
import copy
import json
import asyncio

from app.schemas.action_callback import Action, ActionCallback, SubscriptionActionCallback


class BotController:
    __webhook_data = {
        'update_id': 0,
        'callback_query': {
            'id': '1',
            'from': {
                'id': None,
                'is_bot': False,
                'first_name': '.'
            },
            'message': {
                'message_id': 1,
                'from': {
                    'id': 1,
                    'is_bot': True,
                    'first_name': "bot"
                },
                'chat': {
                    'id': None,
                    'first_name': '.',
                    'type': 'private'
                },
                'date': 1,
                'text': '.'
            },
            'data': 'action:history',
            'chat_instance': '1'
        }
    }

    @classmethod
    def _pack_webhook_data(cls, chat_id: int, data: str) -> str:
        webhookdata = copy.deepcopy(cls.__webhook_data)
        webhookdata['callback_query']['from']['id'] = chat_id
        webhookdata['callback_query']['message']['chat']['id'] = chat_id
        webhookdata['callback_query']['data'] = data
        return json.dumps(webhookdata)

    @classmethod
    async def send_subscription_created(cls, user_telegram_id: int):
        data = SubscriptionActionCallback(action=Action.subscription_add.action, ig_u="", t_id=-1).pack()
        webhook_data = cls._pack_webhook_data(user_telegram_id, data)

        asyncio.create_task(
            app.dispatcher_instance.feed_webhook_update(
                app.bot_instance, app.bot_instance.session.json_loads(webhook_data)
            )
        )

    @classmethod
    async def send_reports(cls, user_telegram_id: int):
        data = ActionCallback(action=Action.report_trackings.action).pack()
        webhook_data = cls._pack_webhook_data(user_telegram_id, data)

        asyncio.create_task(
            app.dispatcher_instance.feed_webhook_update(
                app.bot_instance, app.bot_instance.session.json_loads(webhook_data)
            )
        )

