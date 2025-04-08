from pydantic import BaseModel, ConfigDict, HttpUrl
import datetime as dt


class InstagramUserSchema(BaseModel):
    id: str
    username: str
    full_name: str
    is_private: bool
    biography: str | None = None
    media_count: int | None = None
    followers_count: int | None = None
    following_count: int | None = None

    def is_big(self) -> bool:
        return (self.followers_count or 0) > 20000 or (self.following_count or 0) > 3000


class InstagramUserStatsSchema(BaseModel):
    username: str
    media_count_difference: int
    followers_count_difference: int
    following_count_difference: int
    previous_stats_date: dt.datetime


class InstagramMediaSchema(BaseModel):
    external_id: str
    caption_text: str | None = None
    created_at: dt.datetime
    display_uri: str | None = None

    comment_count: int
    like_count: int
    play_count: int | None = None


class InstagramMediaListSchema(BaseModel):
    items: list[InstagramMediaSchema]
    last_page: bool
    next_max_id: str | None = None


class InstagramMediaStatsSchema(BaseModel):
    external_id: str
    comment_count_current: int
    like_count_current: int
    play_count_current: int | None = None
    comment_count_difference: int
    like_count_difference: int
    play_count_difference: int | None = None
    created_at: dt.datetime | None = None


class InstagramMediaUserStatsSchema(BaseModel):
    like_count_sum: int
    comment_count_sum: int
    play_count_sum: int | None = None
    count: int


class InstagramUserFollowersDifferenceSchema(BaseModel):
    username: str
    subscribes_usernames: list[str]
    unsubscribes_usernames: list[str]
    created_at: dt.datetime


class InstagramUserFollowingDifferenceSchema(BaseModel):
    username: str
    subscribes_usernames: list[str]
    unsubscribes_usernames: list[str]
    created_at: dt.datetime
