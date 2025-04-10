from fastapi import Response, HTTPException
import datetime as dt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
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

    tariffs = [{"id": 1, "price": 200, "access_days": 30, "text": "200 руб. за месяц"}]
    tariffs_big_tracking = [{"id": 1, "price": 590, "access_days": 30, "text": "1 отчет в день за 590 руб."}]

    async def get_tariffs_list(self) -> list:
        return self.tariffs

    async def get_tariffs_big_tracking_list(self) -> list:
        return self.tariffs_big_tracking

    async def create(self, schema: SubscriptionCreateSchema) -> Subscription:
        logger.debug(schema)
        tariff = self.tariffs[schema.tariff_id - 1]
        expire_at = dt.datetime.now() + dt.timedelta(days=tariff["access_days"])
        model = await self._create(
            user_telegram_id=schema.user_telegram_id,
            expire_at=expire_at,
            tariff_id=schema.tariff_id,
        )
        await self._commit()
        await BotController.send_subscription_created(schema.user_telegram_id)
        return model

    async def create_big_tracking(self, schema: SubscriptionCreateSchema) -> Subscription:
        tariff = self.tariffs_big_tracking[schema.tariff_id]
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

    async def _commit(self, force: bool = False):
        """
        Commit changes.
        Handle sqlalchemy.exc.IntegrityError.
        If exception is not found error,
        then throw HTTPException with 404 status (Not found).
        Else log exception and throw HTTPException with 409 status (Conflict)
        """
        try:
            await self.session.commit()
        except exc.IntegrityError as e:
            await self.session.rollback()
            if 'is not present in table' not in str(e.orig):
                logger.exception(e)
                raise HTTPException(status_code=409)
            table_name = str(e.orig).split('is not present in table')[1]
            table_name = table_name.strip().capitalize()
            table_name = table_name.strip('"').strip("'")
            raise HTTPException(
                status_code=404,
                detail=f'{table_name} not found'
            )
