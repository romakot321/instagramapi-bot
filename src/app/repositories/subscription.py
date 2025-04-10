from sqlalchemy import select
import datetime as dt

from app.repositories.base import BaseRepository
from db.tables import Subscription


class SubscriptionRepository[Table: Subscription, int](BaseRepository):
    base_table = Subscription

    async def create(self, **kwargs) -> Subscription:
        return await self._create(**kwargs)

    async def get(self, user_telegram_id: int, tracking_username: str) -> Subscription:
        return await self._get_one(user_telegram_id=user_telegram_id, tracking_username=tracking_username)

    async def get_by_telegram_id(self, telegram_id: int, active: bool = False) -> list[Subscription]:
        query = select(self.base_table).filter_by(user_telegram_id=telegram_id)
        if active:
            query = query.filter(Subscription.expire_at > dt.datetime.now())
        query = self._query_add_select_in_load(query, Subscription.tariff)
        return list(await self.session.scalars(query))

    async def update(self, model_id: int, **fields) -> Subscription:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

    async def list(self, user_telegram_id: int | None = None, page=None, count=None) -> list[Subscription]:
        return list(await self._get_list(user_telegram_id=user_telegram_id, page=page, count=count))

    async def count(self) -> int:
        return await self._count()
