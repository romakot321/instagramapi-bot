from sqlalchemy import select

from app.repositories.base import BaseRepository
from db.tables import Tariff


class TariffRepository[Table: Tariff, int](BaseRepository):
    base_table = Tariff

    async def create(self, **kwargs) -> Tariff:
        return await self._create(**kwargs)

    async def list(self, page=None, count=None) -> list[Tariff]:
        return await self._get_list(page=page, count=count)

    async def get(self, model_id: int) -> Tariff:
        return await self._get_one(id=model_id)

    async def update(self, model_id: int, **fields) -> Tariff:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

    async def count(self) -> int:
        return await self._count()
