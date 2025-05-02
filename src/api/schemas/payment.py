from enum import Enum
from pydantic import BaseModel, Field, model_validator
from urllib.parse import unquote
import datetime as dt


class PaymentProduct(Enum):
    requests_add = "requests"
    subscription_renewal = "subscription"


class PaymentDataSchema(BaseModel):
    user_telegram_id: int
    tariff_id: int
    product: PaymentProduct
    tracking_username: str | None = None


class PaymentSchema(BaseModel):
    transaction_id: int = Field(validation_alias="TransactionId")
    amount: float = Field(validation_alias="Amount")
    currency: str = Field(validation_alias="Currency")
    payment_amount: str = Field(validation_alias="PaymentAmount")
    payment_currency: str = Field(validation_alias="PaymentCurrency")
    datetime: dt.datetime = Field(validation_alias="DateTime")
    email: str = Field(validation_alias="Email")
    invoice_id: str | None = Field(default=None, validation_alias="InvoiceId")
    subscription_id: str | None = Field(default=None, validation_alias="SubscriptionId")
    account_id: str | None = Field(default=None, validation_alias="AccountId")
    data: PaymentDataSchema | None = Field(default=None, validation_alias="Data")

    @model_validator(mode="before")
    @classmethod
    def parse_from_string(cls, value) -> dict:
        if isinstance(value, bytes):
            value = value.decode()
        if not isinstance(value, str):
            return value
        items = unquote(value).split("&")
        state = {key: value for key, value in list(map(lambda i: i.split("="), items))}
        state["DateTime"] = dt.datetime.fromisoformat(state["DateTime"])
        return state
