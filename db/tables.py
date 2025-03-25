from sqlalchemy import BIGINT, ForeignKey, text
from sqlalchemy.orm import Mapped as M, relationship
from sqlalchemy.orm import mapped_column as column
from sqlalchemy_service import Base
import datetime as dt

sql_utcnow = text("(now() at time zone 'utc')")


class BaseMixin:
    id: M[int] = column(primary_key=True, index=True)
    created_at: M[dt.datetime] = column(server_default=sql_utcnow)
    updated_at: M[dt.datetime | None] = column(nullable=True, onupdate=sql_utcnow)


class User(BaseMixin, Base):
    __tablename__ = "users"

    telegram_id: M[int] = column(type_=BIGINT, unique=True)

    trackings: M[list['Tracking']] = relationship(back_populates="creator", lazy="noload")


class Tracking(BaseMixin, Base):
    __tablename__ = "trackings"

    creator_telegram_id: M[int] = column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    instagram_username: M[str]

    creator: M['User'] = relationship(back_populates="trackings", lazy="selectin")

