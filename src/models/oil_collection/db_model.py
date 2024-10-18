from typing import TypeAlias
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from conf.db import Base, timestamp

__all__ = ["UserEntityIdType", "DBUser", "DBUserJoin"]

UserEntityIdType: TypeAlias = UUID


class DBUser(Base):
    __tablename__ = "user"

    status: Mapped[str]
    state: Mapped[str]
    contract_type: Mapped[str]
    pause_start_date: Mapped[timestamp | None]
    pause_end_date: Mapped[timestamp | None]
    cancellation_date: Mapped[timestamp | None]
    active_date: Mapped[timestamp | None]
    expiration_date: Mapped[timestamp | None]
    provider_reference: Mapped[str | None]
    quote_id: Mapped[UUID | None]
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id"))
    viewed_at: Mapped[timestamp]
    notified: Mapped[bool]
    revision: Mapped[int]
    payload: Mapped[dict] = mapped_column(type_=JSONB)
    stripe_subscription_id: Mapped[str | None]


class DBUserJoin(DBUser):
    covers: Mapped[list] = relationship("DBUserCoverJoin", back_populates="user", lazy="selectin")
    pauses: Mapped[list] = relationship("DBUserPauseJoin", back_populates="user", lazy="selectin")
    insurance_provider_quote: Mapped[DBInsuranceProviderQuote | None] = relationship("DBInsuranceProviderQuote",
                                                                                     lazy="joined")
