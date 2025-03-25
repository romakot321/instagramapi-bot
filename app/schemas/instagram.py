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
    caption_text: str | None = None
    created_at: dt.datetime | None = None
    display_uri: str | None = None

    comment_count: int
    like_count: int
    play_count: int | None = None

