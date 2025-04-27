from sqlalchemy import BIGINT, ForeignKey, UniqueConstraint, false, func, select, text, true
from sqlalchemy.orm import Mapped as M, relationship
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_service import Base
from sqlalchemy_service.base_db.base import ServiceEngine
import datetime as dt

sql_utcnow = text("(now() at time zone 'utc')")

engine = ServiceEngine()


class BaseMixin:
    id: M[int] = column(primary_key=True, index=True)
    created_at: M[dt.datetime] = column(server_default=sql_utcnow)
    updated_at: M[dt.datetime | None] = column(nullable=True, onupdate=sql_utcnow)


class FlowUserAssociation(BaseMixin, Base):
    __tablename__ = "flowvariant_user_association"

    user_id: M[int] = column(ForeignKey("users.id", ondelete="CASCADE"))
    flow_variant_id: M[int] = column(ForeignKey("flow_variants.id", ondelete="CASCADE"))
    screen_name: M[str]

    user: M['User'] = relationship(primaryjoin="User.id == FlowUserAssociation.user_id")


class User(BaseMixin, Base):
    __tablename__ = "users"

    telegram_id: M[int] = column(type_=BIGINT, unique=True)
    telegram_username: M[str | None]
    telegram_name: M[str | None]
    referral_id: M[str | None] = column(ForeignKey("referrals.id", ondelete="SET NULL"))

    trackings: M[list['Tracking']] = relationship(back_populates="creator", lazy="noload")
    subscriptions: M[list['Subscription']] = relationship(back_populates="user", lazy="selectin", cascade="delete")
    referral: M["Referral"] = relationship(back_populates="users", lazy="selectin")
    flow_variants: M[list["FlowVariant"]] = relationship(secondary="flowvariant_user_association", lazy="selectin", back_populates="users", cascade="delete")

    @hybrid_property
    def is_renewal_enabled(self) -> bool | None:
        if not self.subscriptions:
            return
        return any([s.renewal_enabled for s in self.subscriptions])

    @hybrid_property
    def trackings_count(self) -> int:
        return len(self.trackings)

    @trackings_count.expression
    def trackings_count(cls):
        return (
            select(func.count(Tracking.creator_telegram_id))
            .select_from(Tracking)
            .where(Tracking.creator_telegram_id == cls.telegram_id)
            .label("trackings_count")
        )



class Tracking(BaseMixin, Base):
    __tablename__ = "trackings"

    creator_telegram_id: M[int] = column(ForeignKey("users.telegram_id", ondelete="CASCADE"), index=True)
    instagram_username: M[str] = column(index=True)

    creator: M['User'] = relationship(back_populates="trackings", lazy="selectin")

    __table_args__ = (UniqueConstraint("creator_telegram_id", "instagram_username", name="tracking_uq"),)


class TrackingMedia(BaseMixin, Base):
    __tablename__ = "tracking_medias"

    instagram_username: M[str] = column(index=True)
    instagram_id: M[str]
    like_count: M[int | None]
    comment_count: M[int | None]
    caption_text: M[str | None]
    display_uri: M[str | None]

    __table_args__ = (UniqueConstraint("instagram_username", "instagram_id", name="tracking_media_uq"),)


class Tariff(BaseMixin, Base):
    __tablename__ = "tariffs"

    def __init__(self, access_days: int) -> None:
        self.access_days = access_days

    payment_amount: M[int] = column(unique=True)
    access_days: M[int]
    requests_balance: M[int]
    tracking_report_interval: M[str] = column(doc="В секундах")

    subscriptions: M[list["Subscription"]] = relationship(
        back_populates="tariff", lazy="selectin"
    )

    @hybrid_property
    def subscriptions_count(self) -> int:
        return len(self.subscriptions)

    @subscriptions_count.expression
    def subscriptions_count(cls):
        return (
            select(func.count(Subscription.tariff_id))
            .select_from(Subscription)
            .where(Subscription.tariff_id == cls.id)
            .label("subscriptions_count")
        )


class Subscription(BaseMixin, Base):
    __tablename__ = "subscriptions"

    expire_at: M[dt.datetime]
    tariff_id: M[int] = column(ForeignKey("tariffs.id", ondelete="CASCADE"))
    tracking_username: M[str | None]
    user_telegram_id: M[int] = column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    renewal_enabled: M[bool] = column(server_default=true())
    requests_available: M[int]

    user: M["User"] = relationship(back_populates="subscriptions", lazy="selectin")
    tariff: M["Tariff"] = relationship(back_populates="subscriptions", lazy="selectin")


class Partner(BaseMixin, Base):
    __tablename__ = "partners"

    name: M[str] = column(unique=True)
    creator_id: M[int | None] = column(ForeignKey("accounts.id", ondelete="SET NULL"))

    referrals: M[list["Referral"]] = relationship(
        back_populates="partner", lazy="selectin", cascade="delete"
    )
    creator: M["Account"] = relationship(back_populates="partners", lazy="noload")


class Referral(BaseMixin, Base):
    __tablename__ = "referrals"

    id: M[str] = column(
        server_default=text("gen_random_uuid()"), primary_key=True, index=True
    )
    partner_id: M[int] = column(ForeignKey("partners.id", ondelete="CASCADE"))
    name: M[str]

    users: M[list["User"]] = relationship(back_populates="referral", lazy="selectin")
    partner: M["Partner"] = relationship(back_populates="referrals", lazy="noload")

    @hybrid_property
    def users_count(self) -> int:
        return len(self.users)

    @users_count.expression
    def users_count(cls):
        return (
            select(func.count(User.referral_id))
            .select_from(User)
            .where(User.referral_id == cls.id)
            .label("users_count")
        )

    @hybrid_property
    def subscribed_users_count(self) -> int:
        return len([u for u in self.users if u.subscriptions])

    @subscribed_users_count.expression
    def subscribed_users_count(cls):
        return (
            select(func.count(User.referral_id))
            .select_from(User)
            .where(User.referral_id == cls.id)
            .filter(User.subscriptions.any(Subscription.user_telegram_id == User.telegram_id))
            .label("subscribed_users_count")
        )


class Flow(BaseMixin, Base):
    __tablename__ = "flows"

    title: M[str]
    screen_name: M[str]
    is_active: M[bool] = column(server_default=true())

    variants: M[list['FlowVariant']] = relationship(back_populates="flow", lazy="selectin")


class FlowVariant(BaseMixin, Base):
    __tablename__ = "flow_variants"

    title: M[str]
    feature_name: M[str]
    is_active: M[bool] = column(server_default=true())
    flow_id: M[int] = column(ForeignKey("flows.id", ondelete="CASCADE"))

    flow: M["Flow"] = relationship(back_populates="variants", lazy="noload")
    users: M[list["User"]] = relationship(secondary="flowvariant_user_association", lazy="selectin", back_populates="flow_variants")

    @hybrid_property
    def users_count(self) -> int:
        return len(self.users)

    @users_count.expression
    def users_count(cls):
        return (
            select(func.count())
            .select_from(FlowUserAssociation)
            .where(FlowUserAssociation.flow_variant_id == cls.id)
            .label("users_count")
        )

    @hybrid_property
    def subscribed_users_count(self) -> int:
        return len([u for u in self.users if u.subscriptions])

    @subscribed_users_count.expression
    def subscribed_users_count(cls):
        return (
            select(func.count())
            .select_from(FlowUserAssociation)
            .where(FlowUserAssociation.flow_variant_id == cls.id)
            .filter(FlowUserAssociation.user.has(User.subscriptions.any(Subscription.user_id == User.id)))
            .label("subscribed_users_count")
        )


class Account(BaseMixin, Base):
    __tablename__ = "accounts"

    username: M[str]
    password_hash: M[str]

    access_to_statistics: M[bool] = column(server_default=false())
    access_to_users: M[bool] = column(server_default=false())
    access_to_trackings: M[bool] = column(server_default=false())
    access_to_partners: M[bool] = column(server_default=false())
    access_to_experiments: M[bool] = column(server_default=false())

    partners: M[list['Partner']] = relationship(back_populates="creator", lazy="noload")
