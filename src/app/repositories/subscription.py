from sqlalchemy import select
import datetime as dt

from app.repositories.base import BaseRepository
from db.tables import Subscription


class SubscriptionRepository[Table: Subscription, int](BaseRepository):
    base_table = Subscription

    async def create(self, **kwargs) -> Subscription:
        return await self._create(**kwargs)

    async def get(self, model_id: int) -> Subscription:
        return await self._get_one(id=model_id)

    async def get_by_telegram_id(self, telegram_id: int, active: bool = False) -> list[Subscription]:
        query = select(self.base_table).filter_by(user_telegram_id=telegram_id)
        if active:
            query = query.filter(Subscription.expire_at > dt.datetime.now())
        return list(await self.session.scalars(query))

    async def update(self, model_id: int, **fields) -> Subscription:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

    async def list(self, page=None, count=None) -> list[Subscription]:
        return await self._get_list(page=page, count=count)

    async def count(self) -> int:
        return await self._count()
