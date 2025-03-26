from sqlalchemy import BIGINT, ForeignKey, UniqueConstraint, text
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

    telegram_id: M[int] = column(type_=BIGINT, unique=True, index=True)

    trackings: M[list['Tracking']] = relationship(back_populates="creator", lazy="noload")
    trackings_medias: M[list['TrackingMedia']] = relationship(back_populates="creator", lazy="noload")


class Tracking(BaseMixin, Base):
    __tablename__ = "trackings"

    creator_telegram_id: M[int] = column(ForeignKey("users.telegram_id", ondelete="CASCADE"), index=True)
    instagram_username: M[str] = column(index=True)

    creator: M['User'] = relationship(back_populates="trackings", lazy="selectin")

    __table_args__ = (UniqueConstraint("creator_telegram_id", "instagram_username", name="tracking_uq"),)


class TrackingMedia(BaseMixin, Base):
    __tablename__ = "tracking_medias"

    creator_telegram_id: M[int] = column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    instagram_username: M[str] = column(index=True)
    instagram_id: M[str]
    caption_text: M[str | None]
    display_uri: M[str | None]

    creator: M['User'] = relationship(back_populates="trackings_medias", lazy="selectin")

    __table_args__ = (UniqueConstraint("creator_telegram_id", "instagram_username", "instagram_id", name="tracking_media_uq"),)

