from aiohttp import ClientSession
from loguru import logger
import os

from app.schemas.instagram import InstagramMediaListSchema, InstagramMediaSchema, InstagramMediaStatsSchema, InstagramMediaUserStatsSchema, InstagramUserFollowersDifferenceSchema, InstagramUserSchema, InstagramUserStatsSchema


class InstagramRepository:
    API_URL = os.getenv("INSTAGRAM_API_URL")

    async def get_user_info(self, username: str) -> InstagramUserSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/user", params={"username": username})
            assert resp.status in (200, 201), await resp.text()
            body = await resp.json()
        return InstagramUserSchema.model_validate(body)

    async def get_user_followers_difference(self, username: str) -> list[InstagramUserFollowersDifferenceSchema]:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(f"/api/user/{username}/followers")
            if resp.status != 200:
                raise ValueError(await resp.text())
            body = await resp.json()
        return [InstagramUserFollowersDifferenceSchema.model_validate(i) for i in body]

    async def get_user_followers(self, username: str) -> list[InstagramUserSchema]:
        raise DeprecationWarning("Deprecated function")
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

    async def get_user_media_info(self, username: str, max_id: str | None = None) -> InstagramMediaListSchema:
        params = {"username": username, "count": 10}
        if max_id is not None:
            params["max_id"] = max_id
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/media", params=params)
            assert resp.status in (200, 201), await resp.text()
            body = await resp.json()
        return InstagramMediaListSchema.model_validate(body)

    async def get_media_info(self, media_id: str) -> InstagramMediaSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/media/" + media_id)
            if resp.status != 200:
                raise ValueError(await resp.text())
            body = await resp.json()
        return InstagramMediaSchema.model_validate(body)

    async def get_media_stats(self, media_id: str) -> InstagramMediaStatsSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/media/" + media_id + "/stats", params={"days": 7})
            assert resp.status == 200, await resp.text()
            body = await resp.json()
        logger.debug(body)
        return InstagramMediaStatsSchema.model_validate(body)

    async def get_media_user_stats(self, username: str) -> InstagramMediaUserStatsSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/media/stats", params={"days": 7, "username": username})
            assert resp.status == 200, await resp.text()
            body = await resp.json()
        return InstagramMediaUserStatsSchema.model_validate(body)
