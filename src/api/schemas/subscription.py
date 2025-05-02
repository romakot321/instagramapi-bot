from pydantic import BaseModel, Field, model_validator
from urllib.parse import unquote
import datetime as dt


class SubscriptionCreateSchema(BaseModel):
    user_telegram_id: int
    tariff_id: int
    tracking_username: str | None = None


class SubscriptionAddRequestsSchema(BaseModel):
    user_telegram_id: int
    tariff_id: int
    tracking_username: str


class SubscriptionBigTrackingCreateSchema(SubscriptionCreateSchema):
    tracking_username: str
