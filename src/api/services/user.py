import os
from aiohttp import ClientSession
from fastapi import Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService

from app.controller import BotController
from db.tables import User
from db import engine


class UserService[Table: User, int](BaseService):
    base_table = User
    engine = engine
    session: AsyncSession
    response: Response
    instagram_api_url = os.getenv("INSTAGRAM_API_URL")

    @classmethod
    async def create_report(self, telegram_id: int, username: str):
        async with ClientSession(base_url=self.instagram_api_url) as session:
            resp = await session.post(f"/api/user/{username}/report", json={"webhook_url": f"http://instagrambot_app/api/user/{telegram_id}/report"})
            if resp.status != 202:
                raise ValueError("Failed to send create report request: " + await resp.text())

    async def send_report(self, telegram_id: int, username: str):
        await BotController.send_report(telegram_id, username)

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
