from fastapi import Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService

from db.tables import User
from db import engine


class UserService[Table: User, int](BaseService):
    base_table = User
    engine = engine
    session: AsyncSession
    response: Response

    async def create(self, **fields) -> User:
        return await self._create(**fields)

    async def list(self, page=None, count=None) -> list[User]:
        return list(await self._get_list(page=page, count=count, select_in_load=User.trackings))

    async def get(self, model_id: int) -> User:
        return await self._get_one(
            id=model_id
        )

    async def update(self, model_id: int, **fields) -> User:
        return await self._update(model_id, **fields)

    async def count(self):
        return await self._count()
