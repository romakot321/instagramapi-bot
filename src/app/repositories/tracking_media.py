from sqlalchemy import select

from app.repositories.base import BaseRepository
from db.tables import TrackingMedia


class TrackingMediaRepository(BaseRepository):
    base_table = TrackingMedia

    async def create(self, **kwargs) -> TrackingMedia:
        return await self._create(**kwargs)

    async def list(
        self,
        creator_telegram_id: int | None = None,
        instagram_username: str | None = None,
        page=None,
        count=None,
    ) -> list[TrackingMedia]:
        query = self._get_list_query(
            creator_telegram_id=creator_telegram_id,
            instagram_username=instagram_username,
            page=page,
            count=count,
        )
        query = query.order_by(TrackingMedia.created_at.desc())
        return list(await self.session.scalars(query))

    async def get(self, model_id: int) -> TrackingMedia:
        return await self._get_one(id=model_id)

    async def get_by_instagram_id(self, instagram_id: str) -> TrackingMedia:
        return await self._get_one(instagram_id=instagram_id)

    async def update(self, model_id: int, **fields) -> TrackingMedia:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

    async def count(self) -> int:
        return await self._count()
