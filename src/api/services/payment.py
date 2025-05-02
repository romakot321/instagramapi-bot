from fastapi import Response
import datetime as dt
from loguru import logger
from api.schemas.payment import PaymentProduct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService

from db.tables import Payment
from db import engine


class PaymentService[Table: Payment, int](BaseService):
    base_table = Payment
    engine = engine
    session: AsyncSession
    response: Response

    async def create(
        self,
        user_telegram_id: int,
        cloudpayments_transaction_id: int,
        product: PaymentProduct,
        amount: float,
        cloudpayments_subscription_id: str | None = None,
    ) -> Payment:
        model = await self._create(
            user_telegram_id=user_telegram_id,
            cloudpayments_transaction_id=cloudpayments_transaction_id,
            product=product.value,
            amount=amount,
            cloudpayments_subscription_id=cloudpayments_subscription_id,
        )
        return model

    async def list(self, page=None, count=None) -> list[Payment]:
        return list(await self._get_list(page=page, count=count))

    async def get(self, model_id: int) -> Payment:
        return await self._get_one(id=model_id)

    async def update(self, model_id: int, **fields) -> Payment:
        return await self._update(model_id, **fields)

    async def count(self):
        return await self._count()
