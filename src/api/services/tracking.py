from fastapi import Response
import datetime as dt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService

from db.tables import Tracking
from db import engine


class TrackingService[Table: Tracking, int](BaseService):
    base_table = Tracking
    engine = engine
    session: AsyncSession
    response: Response

    async def create(self, creator_telegram_id: int, tracking_username: str) -> Tracking:
        model = await self._create(
            creator_telegram_id=creator_telegram_id,
            tracking_username=tracking_username
        )
        return model

    async def list(self, page=None, count=None) -> list[Tracking]:
        return list(await self._get_list(page=page, count=count))

    async def get(self, model_id: int) -> Tracking:
        return await self._get_one(id=model_id)

    async def update(self, model_id: int, **fields) -> Tracking:
        return await self._update(model_id, **fields)

    async def count(self):
        return await self._count()
