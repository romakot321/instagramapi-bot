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
    add_tracking = ButtonData(action="add_tracking", text="Добавить профиль")
    show_trackings = ButtonData(action="show_trackings", text="Мои профили")
    subscription_menu = ButtonData(action="subscription_menu", text="Подписка")

    tracking_followers = ButtonData(action="tracking_followers", text="Подписчики")
    tracking_stats = ButtonData(action="tracking_stats", text="Статистика")
    tracking_show = ButtonData(action="tracking_show", text=None)

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
    page: int = 0


class TrackingActionCallback(PaginatedActionCallback, prefix="tracking_action"):
    username: str
