from pydantic import BaseModel


class SubscriptionCreateSchema(BaseModel):
    user_telegram_id: int
    tariff_id: int


class SubscriptionBigTrackingCreateSchema(SubscriptionCreateSchema):
    tracking_username: str
