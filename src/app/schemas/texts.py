import re

from app.schemas.instagram import InstagramMediaSchema, InstagramMediaStatsSchema, InstagramUserSchema, InstagramUserStatsSchema
from db.tables import Subscription, TrackingMedia


def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    ret = re.sub(r"([{}])".format(re.escape(escape_chars)), r"\\\1", text)
    for i in "_*[]()~`>#+-=|{}.!":
        ret = ret.replace(f"\\{i}\\{i}", i)
    return ret


_start_text = """
Это бот для аналитики статистики пользователя инстаграмм.
Чтобы начать, добавьте нового пользователя
"""
start_text = escape_markdown(_start_text)


_user_info_text = """
Никнейм: {schema.username}
Имя: {schema.full_name}
Постов: {schema.media_count}
Подписчиков: {schema.followers_count}
Подписок: {schema.following_count}
"""

_user_info_masked_text = """
Никнейм: {schema.username}
Имя: {schema.full_name}
Постов: ###
Подписчиков: {schema.followers_count}
Подписок: {schema.following_count}

Некоторые данные скрыты
"""

_user_stats_text = """
Статистика от {schema.previous_stats_date}
Изменение постов: {schema.media_count_difference}
Изменение подписчиков: {schema.followers_count_difference}
Изменение подписок: {schema.following_count_difference}
"""

_user_follower_text = """{user.full_name} (@{user.username})"""


def build_user_info_text(schema: InstagramUserSchema) -> str:
    return _user_info_text.format(schema=schema)


def build_user_info_masked_text(schema: InstagramUserSchema) -> str:
    return _user_info_masked_text.format(schema=schema)


def build_user_stats_text(schema: InstagramUserStatsSchema) -> str:
    return _user_stats_text.format(schema=schema)


def build_user_followers_text(followers: list[InstagramUserSchema]) -> str:
    return "\n".join(_user_follower_text.format(user=user) for user in followers)


_media_stats_text = """
{media.caption_text}
Статистика от {stats.created_at}
- Комментариев: {stats.comment_count_difference}
- Лайков: {stats.like_count_difference}
- Просмотров: {stats.play_count_difference}
"""


def build_media_stats_text(stats: InstagramMediaStatsSchema, media: TrackingMedia) -> str:
    return _media_stats_text.format(media=media, stats=stats)


_subscription_info_text = """
Подписка активна до {subscription.expire_at}
"""

subscription_paywall_text = """
Оформите подписку для продолжения
"""


def build_subscription_info_text(subscription: Subscription) -> str:
    return _subscription_info_text.format(subscription=subscription)
