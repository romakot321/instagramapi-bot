import re

from app.schemas.instagram import InstagramMediaSchema, InstagramUserSchema, InstagramUserStatsSchema


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

_user_stats_text = """
Статистика от {schema.previous_stats_date}
Изменение постов: {schema.media_count_difference}
Изменение подписчиков: {schema.followers_count_difference}
Изменение подписок: {schema.following_count_difference}
"""

_user_follower_text = """{user.full_name} (@{user.username})"""

def build_user_info_text(schema: InstagramUserSchema) -> str:
    return _user_info_text.format(schema=schema)


def build_user_stats_text(schema: InstagramUserStatsSchema) -> str:
    return _user_stats_text.format(schema=schema)


def build_user_followers_text(followers: list[InstagramUserSchema]) -> str:
    return "\n".join(_user_follower_text.format(user=user) for user in followers)


_media_info_text = """
Пост {schema.title}
{schema.caption_text}
Тип поста: {schema.media_type}
Комментариев: {schema.comment_count}
Лайков: {schema.like_count}
Запусков: {schema.play_count}
Просмотров: {schema.view_count}
Ссылки:
{urls}
"""


def build_media_info_text(schema: InstagramMediaSchema) -> str:
    urls = str(schema.thumbnail_url) if schema.thumbnail_url else ""
    for resource in schema.resources:
        urls += "\n" + str(resource.thumbnail_url)

    return _media_info_text.format(schema=schema, urls=urls)


def build_media_info_list_text(schemas: list[InstagramMediaSchema]) -> str:
    return "\n\n".join(build_media_info_text(schema) for schema in schemas)
