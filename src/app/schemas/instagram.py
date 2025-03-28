from pydantic import BaseModel, ConfigDict, HttpUrl
import datetime as dt


class InstagramUserSchema(BaseModel):
    id: str
    username: str
    full_name: str
    media_count: int | None = None
    followers_count: int | None = None
    following_count: int | None = None


class InstagramUserStatsSchema(BaseModel):
    username: str
    media_count_difference: int
    followers_count_difference: int
    following_count_difference: int
    previous_stats_date: dt.datetime


class InstagramMediaSchema(BaseModel):
    external_id: str
    caption_text: str | None = None
    created_at: dt.datetime | None = None
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
    comment_count_difference: int
    like_count_difference: int
    play_count_difference: int | None = None
    created_at: dt.datetime | None = None


class InstagramMediaUserStatsSchema(BaseModel):
    like_count_sum: int
    comment_count_sum: int
    play_count_sum: int
    count: int
