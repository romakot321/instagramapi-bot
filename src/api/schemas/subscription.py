from pydantic import BaseModel


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
