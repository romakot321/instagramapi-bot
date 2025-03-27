from fastapi import Response
import datetime as dt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService

from api.schemas.subscription import SubscriptionCreateSchema
from app.controller import BotController
from db.tables import Subscription
from db import engine


class SubscriptionService[Table: Subscription, int](BaseService):
    base_table = Subscription
    engine = engine
    session: AsyncSession
    response: Response

    tariffs = [{"id": 0, "price": 200, "access_days": 30, "text": "200 руб. за месяц"}]

    async def get_tariffs_list(self) -> list:
        return self.tariffs

    async def create(self, schema: SubscriptionCreateSchema) -> Subscription:
        tariff = self.tariffs[schema.tariff_id]
        expire_at = dt.datetime.now() + dt.timedelta(days=tariff["access_days"])
        model = await self._create(
            user_telegram_id=schema.user_telegram_id,
            expire_at=expire_at,
            tariff_id=schema.tariff_id,
        )
        await BotController.send_subscription_created(schema.user_telegram_id)
        return model

    async def list(self, page=None, count=None) -> list[Subscription]:
        return list(await self._get_list(page=page, count=count))

    async def get(self, model_id: int) -> Subscription:
        return await self._get_one(id=model_id)

    async def update(self, model_id: int, **fields) -> Subscription:
        return await self._update(model_id, **fields)

    async def count(self):
        return await self._count()
