from sqlalchemy import select

from app.repositories.base import BaseRepository
from db.tables import Tracking


class TrackingRepository[Table: Tracking, int](BaseRepository):
    base_table = Tracking

    async def create(self, **kwargs) -> Tracking:
        return await self._create(**kwargs)

    async def list(
        self, creator_telegram_id: int | None = None, page=None, count=None
    ) -> list[Tracking]:
        return list(
            await self._get_list(
                page=page, count=count, creator_telegram_id=creator_telegram_id
            )
        )

    async def get(
        self,
        creator_telegram_id: int,
        instagram_username: str,
        mute_not_found_exception: bool = False,
    ) -> Tracking:
        return await self._get_one(
            creator_telegram_id=creator_telegram_id,
            instagram_username=instagram_username,
            mute_not_found_exception=mute_not_found_exception,
        )

    async def update(self, model_id: int, **fields) -> Tracking:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

    async def count(self, creator_telegram_id: int | None = None) -> int:
        return await self._count(creator_telegram_id=creator_telegram_id)
