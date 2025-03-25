from aiohttp import ClientSession
import os

from app.schemas.instagram import InstagramMediaSchema, InstagramUserSchema, InstagramUserStatsSchema


class InstagramRepository:
    API_URL = os.getenv("INSTAGRAM_API_URL")

    async def get_user_info(self, username: str) -> InstagramUserSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/user", params={"username": username})
            assert resp.status in (200, 201), await resp.text()
            body = await resp.json()
        return InstagramUserSchema.model_validate(body)

    async def get_user_followers(self, username: str) -> list[InstagramUserSchema]:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/user/" + username + "/followers")
            assert resp.status == 200, await resp.text()
            body = await resp.json()
        return [InstagramUserSchema.model_validate(user) for user in body]

    async def get_user_stats(self, username: str) -> InstagramUserStatsSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/user/" + username + "/stats", params={"days": 7})
            assert resp.status == 200, await resp.text()
            body = await resp.json()
        return InstagramUserStatsSchema.model_validate(body)

    async def get_user_media_info(self, username: str) -> list[InstagramMediaSchema]:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/media", params={"username": username})
            assert resp.status == 200, await resp.text()
            body = await resp.json()
        return [
            InstagramMediaSchema.model_validate(item)
            for item in body
        ]
