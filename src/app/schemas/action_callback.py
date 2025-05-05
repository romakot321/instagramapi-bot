from enum import Enum

from aiogram.filters.callback_data import CallbackData
from pydantic import BaseModel, Field, AliasChoices, computed_field


class ButtonData(BaseModel):
    text: str | None = None
    action: str = Field(exclude=True)

    @computed_field
    def callback_data(self) -> str:
        return ActionCallback(action=self.action).pack()


class Action(Enum):
    main_menu = ButtonData(action="main_menu", text="В меню")
    delete_message = ButtonData(action="delete_message", text="Закрыть")

    add_tracking = ButtonData(action="add_tracking", text="Добавить отслеживание")
    show_trackings = ButtonData(action="show_trackings", text="Мои отслеживания")
    subscription_menu = ButtonData(action="subscription_menu", text="Подписка")
    support_menu = ButtonData(action="subscription_menu", text="Поддержка")
    report_trackings = ButtonData(action="report_trackings", text=None)

    tracking_subscribe = ButtonData(action="t_subscribe", text="🟢 Подписаться")
    tracking_unsubscribe = ButtonData(action="t_unsubscribe", text="🔴 Отписаться")
    tracking_collect_data = ButtonData(action="t_collect", text="Запустить сбор данных")
    tracking_followers = ButtonData(action="t_followers", text="Подписчики")
    tracking_followers_following_collision = ButtonData(action="t_fwr_fng_col", text="Взаимные подписки")
    tracking_followers_following_difference = ButtonData(action="t_fwr_fng_diff", text="Невзаимные подписчики")
    tracking_following_followers_difference = ButtonData(action="t_fng_fwr_diff", text="Невзаимные подписки")
    tracking_hidden_followers = ButtonData(action="t_hidden_fwrs", text="Тайные поклонники")
    tracking_new_subscribers = ButtonData(action="t_new_subrs", text="🧑‍💻 Кто подписался")
    tracking_new_unsubscribed = ButtonData(action="t_new_unsubd", text="⭐ Кто отписался")
    tracking_subscribtions = ButtonData(action="t_new_subns", text="🧑‍💻 На кого подписался")
    tracking_unsubscribes = ButtonData(action="t_new_unsubes", text="⭐ От кого отписался")
    tracking_top_followers = ButtonData(action="t_top_folws", text="Самые активные подписчики")
    tracking_stats = ButtonData(action="t_stats", text="📊Посмотреть полную статистику пользователя")
    tracking_show = ButtonData(action="t_show", text=None)
    tracking_settings = ButtonData(action="t_settings", text="Настройки")
    tracking_report_interval = ButtonData(action="t_rep_interval", text=None)
    show_tracking_media = ButtonData(action="media", text="Публикации")

    tracking_media_stats = ButtonData(action="media_stats", text="Статистика")
    tracking_media_display = ButtonData(action="media_display", text="Посмотреть")

    subscription_add = ButtonData(action="subscription_add", text="Приобрести подписку")
    subscription_created = ButtonData(action="subscription_created", text=None)
    subscription_cancel = ButtonData(action="subscription_cancel", text="Отменить автопродление")
    subscription_add_trackings = ButtonData(action="subscription_add_trackings", text="Купить отслеживания")

    def __init__(self, value: ButtonData):
        self.action = value.action
        self.text = value.text

    def model_dump(self) -> dict:
        return self.value.model_dump()


class ActionCallback(CallbackData, prefix='action'):
    """
    :param action: str, action_name from Action enum
    """
    action: str

    @classmethod
    def copy(cls):
        return cls(**cls.__dict__)

    def replace(self, **values):
        """Return new object with replaced values"""
        new_state = self.__dict__ | values
        return self.__class__(**new_state)


class PaginatedActionCallback(ActionCallback, prefix='paginated_action'):
    """
    :param page: int OR None, current page
    """
    page: int = 1


class TrackingActionCallback(PaginatedActionCallback, prefix="t_action"):
    username: str | None


class TrackingMediaActionCallback(PaginatedActionCallback, prefix="m_action"):
    instagram_id: str
    media_page: int = 1


class SubscriptionActionCallback(ActionCallback, prefix="s_action"):
    ig_u: str | None # Instagram username
    t_id: int  # Tariff id


class TrackingReportCallback(PaginatedActionCallback, prefix="t_report"):
    username: str
    report_id: int
