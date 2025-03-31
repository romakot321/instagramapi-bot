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
    add_tracking = ButtonData(action="add_tracking", text="Добавить отслеживание")
    show_trackings = ButtonData(action="show_trackings", text="Мои отслеживания")
    subscription_menu = ButtonData(action="subscription_menu", text="Подписка")
    report_trackings = ButtonData(action="report_trackings", text=None)

    tracking_subscribe = ButtonData(action="tracking_subscribe", text="Подписаться")
    tracking_unsubscribe = ButtonData(action="tracking_subscribe", text="Отписаться")
    tracking_followers = ButtonData(action="tracking_followers", text="Подписчики")
    tracking_stats = ButtonData(action="tracking_stats", text="Статистика")
    tracking_show = ButtonData(action="tracking_show", text=None)
    show_tracking_media = ButtonData(action="media", text="Публикации")

    tracking_media_stats = ButtonData(action="media_stats", text="Статистика")

    subscription_add = ButtonData(action="subscription_add", text="Приобрести подписку")
    subscription_cancel = ButtonData(action="subscription_cancel", text="Отменить подписку")
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


class TrackingActionCallback(PaginatedActionCallback, prefix="tracking_action"):
    username: str


class TrackingMediaActionCallback(PaginatedActionCallback, prefix="media_action"):
    instagram_id: str


class SubscriptionActionCallback(ActionCallback, prefix="subscription_action"):
    pass
