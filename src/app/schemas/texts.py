import re

from app.schemas.instagram import (
    InstagramMediaSchema,
    InstagramMediaStatsSchema,
    InstagramMediaUserStatsSchema,
    InstagramUserSchema,
    InstagramUserStatsSchema,
)
from db.tables import Subscription, TrackingMedia


def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    ret = re.sub(r"([{}])".format(re.escape(escape_chars)), r"\\\1", text)
    for i in "_*[]()~`>#+-=|{}.!":
        ret = ret.replace(f"\\{i}\\{i}", i)
    return ret


_start_text = """
Привет! 👋 Добро пожаловать в [Название бота] – твой личный помощник для анализа статистики Instagram.

**С моей помощью ты сможешь отслеживать:**
📈 Рост подписчиков
❤️  Лайки и комментарии
📊 Вовлеченность
📅 Лучшее время для публикаций
и многое другое!

Чтобы начать, выполни несколько простых шагов:

1. Выбери аккаунт для анализа, нажав на кнопку "Добавить отслеживание"
2. Получи первую статистику нажав на кнопку "Статистика"

__Готов начать?__
"""
start_text = escape_markdown(_start_text)


_tracking_info_text = """
📱  Никнейм: {schema.username}
🔗  Ссылка на аккаунт: instagram.com/{schema.username}
📛  Имя: {schema.full_name}
🧑‍💻  Подписчиков: {schema.followers_count}
⭐️  Подписок: {schema.following_count}
🖼  Постов: {schema.media_count}
ℹ️  Описание: TODO
"""

_tracking_info_masked_text = """
Никнейм: {schema.username}
Имя: {schema.full_name}
Постов: ###
Подписчиков: {schema.followers_count}
Подписок: {schema.following_count}

Некоторые данные и статистика скрыты
"""

_tracking_stats_text = """
📊 **Текущая статистика**:
🖼 Количество постов: {media_count}
👍 В среднем лайков на пост: {media_likes}
⌨️ В среднем комментариев на пост: {media_comments}
🤔 Коэф. вовлеченности: {media_coeff}%

📊 **Статистика изменений от {change.previous_stats_date:%d.%m.%Y %H:%M}**
🖼 Изменение постов: {change.media_count_difference}
🧑‍💻 Изменение подписчиков: 🔽 {change.followers_count_difference}
⭐️ Изменение подписок: 🔽 {change.following_count_difference}
"""

_tracking_follower_text = """instagram.com/{tracking}"""

_tracking_report_text = """
Отчет по пользователю: @{tracking.username}

Ссылка на аккаунт: https://www.instagram.com/{tracking.username}

📊 Статистика от 31.03.2025 17:47

🖼 Количество постов: 🔼{media_count} ({change.media_count_difference})
🧑‍💻 Количество подписчиков: 🔽{tracking.followers_count} ({change.followers_count_difference})
⭐️ Количество подписок: 🔼{tracking.following_count} ({change.following_count_difference})
"""


def build_tracking_info_text(schema: InstagramUserSchema) -> str:
    return _tracking_info_text.format(schema=schema)


def build_tracking_info_masked_text(schema: InstagramUserSchema) -> str:
    return _tracking_info_masked_text.format(schema=schema)


def build_tracking_stats_text(
    change: InstagramUserStatsSchema,
    current: InstagramMediaUserStatsSchema,
    tracking: InstagramUserSchema,
) -> str:
    text = _tracking_stats_text.format(
        media_count=current.count,
        media_likes=round(current.like_count_sum / current.count, 2),
        media_comments=round(current.comment_count_sum / current.count, 2),
        media_coeff=round(
            (current.like_count_sum + current.comment_count_sum)
            / tracking.followers_count
            * 100,
            2,
        ),
        change=change,
    )
    return escape_markdown(text)


def build_tracking_followers_text(followers: list[str]) -> str:
    return "\n".join(
        _tracking_follower_text.format(tracking=tracking) for tracking in followers
    )


def build_tracking_report_text(
    change: InstagramUserStatsSchema,
    current: InstagramMediaUserStatsSchema,
    tracking: InstagramUserSchema,
) -> str:
    return _tracking_report_text.format(
        media_count=current.count,
        media_likes=round(current.like_count_sum / current.count, 2),
        media_comments=round(current.comment_count_sum / current.count, 2),
        media_coeff=round(
            (current.like_count_sum + current.comment_count_sum)
            / tracking.followers_count
            * 100,
            2,
        ),
        change=change,
        tracking=tracking,
    )


_media_stats_text = """
{media.caption_text}
Текущая статистика:
- Комментариев: {stats.comment_count_current}
- Лайков: {stats.like_count_current}
- Просмотров: {stats.play_count_current}

Статистика изменений от {stats.created_at:%d.%m.%Y %H:%M}
- Комментариев: {stats.comment_count_difference}
- Лайков: {stats.like_count_difference}
- Просмотров: {stats.play_count_difference}
"""


def build_media_stats_text(
    stats: InstagramMediaStatsSchema, media: TrackingMedia
) -> str:
    return _media_stats_text.format(media=media, stats=stats)


_subscription_info_text = """
Подписка активна до {subscription.expire_at:%d.%m.%Y %H:%M}
"""

subscription_paywall_text = """
Оформите подписку для продолжения
"""


def build_subscription_info_text(subscription: Subscription) -> str:
    return _subscription_info_text.format(subscription=subscription)
