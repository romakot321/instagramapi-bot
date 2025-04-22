from aiohttp import ClientSession
from loguru import logger
import os

from app.schemas.exception import ApiException

from app.schemas.instagram import (
    InstagramMediaListSchema,
    InstagramMediaSchema,
    InstagramMediaStatsSchema,
    InstagramMediaUserStatsSchema,
    InstagramUserFollowDifferenceSchema,
    InstagramUserFollowersDifferenceSchema,
    InstagramUserFollowingDifferenceSchema,
    InstagramUserReportSchema,
    InstagramUserSchema,
    InstagramUserStatsSchema,
)


class InstagramRepository:
    API_URL = os.getenv("INSTAGRAM_API_URL")

    async def start_user_tracking(self, username: str) -> InstagramUserSchema | str:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.post("/api/user", json={"instagram_username": username})
            if resp.status in (200, 201):
                return InstagramUserSchema.model_validate(await resp.json())
            elif resp.status == 404:
                return "Профиль не найден"
            elif resp.status == 400:
                return (await resp.json())["detail"]
            raise ApiException(await resp.text())

    async def get_user_info(self, username: str) -> InstagramUserSchema | None:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/user", params={"username": username})
            if resp.status in (200, 201):
                body = await resp.json()
                return InstagramUserSchema.model_validate(body)
            elif resp.status == 404:
                return None
            raise ApiException(await resp.text())

    async def get_user_reports(self, username: str) -> list[InstagramUserReportSchema]:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/user/" + username + "/report")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return [
            InstagramUserReportSchema.model_validate(i)
            for i in body
        ]

    async def get_user_followers_difference(
        self, username: str
    ) -> list[InstagramUserFollowersDifferenceSchema]:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(f"/api/user/{username}/followers")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return [InstagramUserFollowersDifferenceSchema.model_validate(i) for i in body]

    async def get_user_following_difference(
        self, username: str
    ) -> list[InstagramUserFollowingDifferenceSchema]:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(f"/api/user/{username}/following")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return [InstagramUserFollowingDifferenceSchema.model_validate(i) for i in body]

    async def get_user_followers_following_difference(self, username: str) -> InstagramUserFollowDifferenceSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(f"/api/user/{username}/followers/following")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramUserFollowDifferenceSchema.model_validate(body)

    async def get_user_following_followers_difference(self, username: str) -> InstagramUserFollowDifferenceSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(f"/api/user/{username}/following/followers")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramUserFollowDifferenceSchema.model_validate(body)

    async def get_user_following_followers_collision(self, username: str) -> InstagramUserFollowDifferenceSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(f"/api/user/{username}/followers_following")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramUserFollowDifferenceSchema.model_validate(body)

    async def get_user_hidden_followers(self, username: str) -> InstagramUserFollowDifferenceSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(f"/api/user/{username}/hidden_followers")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramUserFollowDifferenceSchema.model_validate(body)

    async def get_user_followers(self, username: str) -> list[InstagramUserSchema]:
        raise DeprecationWarning("Deprecated function")
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/user/" + username + "/followers")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return [InstagramUserSchema.model_validate(user) for user in body]

    async def get_user_stats(self, username: str) -> InstagramUserStatsSchema | str:
        """Return schema or error text"""
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(
                "/api/user/" + username + "/stats", params={"days": 7}
            )
            if resp.status == 400:
                body = await resp.json()
                return body.get("detail", "Внутреняя ошибка")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramUserStatsSchema.model_validate(body)

    async def get_user_stats_change_from_real(self, username: str, days: int = 1) -> InstagramUserStatsSchema | str:
        """Return schema or error text"""
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(
                "/api/user/" + username + "/change", params={"days": days}
            )
            if resp.status == 400:
                body = await resp.json()
                return body.get("detail", "Внутреняя ошибка")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramUserStatsSchema.model_validate(body)

    async def get_user_media_info(
            self, username: str, count: int = 12, max_id: str | None = None
    ) -> InstagramMediaListSchema:
        params = {"username": username, "count": count}
        if max_id is not None:
            params["max_id"] = max_id
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/media", params=params)
            if resp.status not in (200, 201):
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramMediaListSchema.model_validate(body)

    async def get_media_info(self, media_id: str) -> InstagramMediaSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get("/api/media/" + media_id)
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramMediaSchema.model_validate(body)

    async def get_media_stats(
        self, media_id: str, days: int = 7
    ) -> InstagramMediaStatsSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(
                "/api/media/" + media_id + "/stats", params={"days": days}
            )
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        logger.debug(body)
        return InstagramMediaStatsSchema.model_validate(body)

    async def get_media_user_stats(
        self, username: str, days: int = 7
    ) -> InstagramMediaUserStatsSchema | str:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.get(
                "/api/media/stats", params={"days": days, "username": username}
            )
            if resp.status == 400:
                body = await resp.json()
                return body.get("detail", "Внутреняя ошибка")
            if resp.status != 200:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramMediaUserStatsSchema.model_validate(body)

    async def create_user_report(self, telegram_id: int, username: str, force: bool = False) -> InstagramUserReportSchema:
        async with ClientSession(base_url=os.getenv("INSTAGRAM_API_URL")) as session:
            resp = await session.post(f"/api/user/{username}/report", json={"webhook_url": f"http://instagrambot_app/api/user/{telegram_id}/report", "force": force})
            if resp.status != 201:
                raise ApiException(await resp.text())
            body = await resp.json()
        return InstagramUserReportSchema.model_validate(body)
