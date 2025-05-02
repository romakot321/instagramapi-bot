from fastapi import Response, HTTPException, Request
import datetime as dt
import os
import hmac
import hashlib
import base64
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from sqlalchemy_service import BaseService

from api.schemas.subscription import SubscriptionAddRequestsSchema, SubscriptionCreateSchema
from app.controller import BotController
from db.tables import Subscription, Tariff
from db import engine


class SubscriptionService[Table: Subscription, int](BaseService):
    base_table = Subscription
    engine = engine
    session: AsyncSession
    response: Response

    tariffs_big_tracking = [{"id": 1, "price": 590, "access_days": 30, "text": "1 отчет в день за 590 руб."}]
    CLOUDPAYMENTS_API_TOKEN = os.getenv("CLOUDPAYMENTS_API_TOKEN")

    @classmethod
    async def authorize_cloudpayments_webhook(cls, request: Request):
        signature = base64.b64encode(hmac.new(cls.CLOUDPAYMENTS_API_TOKEN.encode(), await request.body(), digestmod=hashlib.sha256).digest())
        if signature.decode() != request.headers["Content-HMAC"]:
            raise HTTPException(401)

    async def get_tariffs_list(self) -> list[Tariff]:
        query = select(Tariff)
        return list(await self.session.scalars(query))

    async def get_tariffs_big_tracking_list(self) -> list:
        return self.tariffs_big_tracking

    async def get_tariff(self, tariff_id: int) -> Tariff:
        query = select(Tariff).filter_by(id=tariff_id)
        model = await self.session.scalar(query)
        if model is None:
            raise HTTPException(404)
        return model

    async def create(self, schema: SubscriptionCreateSchema, cloudpayments_subscription_id: str) -> Subscription:
        if schema.tracking_username:
            current_subscription = await self._get_one(tracking_username=schema.tracking_username, user_telegram_id=schema.user_telegram_id, mute_not_found_exception=True)
            if current_subscription is not None:
                model = await self._update(
                    current_subscription.id,
                    tariff_id=schema.tariff_id
                )
                await BotController.send_subscription_created(schema.user_telegram_id, schema.tracking_username)
                return model

        tariff = await self.get_tariff(schema.tariff_id)
        expire_at = dt.datetime.now() + dt.timedelta(days=tariff.access_days)

        model = await self._create(
            user_telegram_id=schema.user_telegram_id,
            expire_at=expire_at,
            tracking_username=schema.tracking_username,
            tariff_id=schema.tariff_id,
            requests_available=tariff.requests_balance,
            cloudpayments_subscription_id=cloudpayments_subscription_id,
            cloudpayments_transaction_id=cloudpayments_transaction_id
        )
        await self._commit()

        await BotController.send_subscription_created(schema.user_telegram_id, schema.tracking_username)
        return model

    async def add_requests(self, schema: SubscriptionAddRequestsSchema) -> Subscription:
        tariff = await self.get_tariff(schema.tariff_id)
        subscription = await self.get(schema.user_telegram_id, schema.tracking_username)
        model = await self.update(subscription.id, requests_available=subscription.requests_available + tariff.requests_balance)
        await BotController.send_subscription_created(schema.user_telegram_id, schema.tracking_username)
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
        return list(await self._get_list(page=page, count=count, select_in_load=Subscription.tariff))

    async def get(self, user_telegram_id: int, tracking_username: str) -> Subscription:
        return await self._get_one(user_telegram_id=user_telegram_id, tracking_username=tracking_username)

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
