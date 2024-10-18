from typing import TypeAlias
from uuid import UUID

from sqlalchemy.orm import Mapped

from conf.db import Base, timestamp

__all__ = ["UserEntityIdType", "DBUser"]

UserEntityIdType: TypeAlias = UUID


class DBUser(Base):
    __tablename__ = "user"

    first_name: Mapped[str]
    last_name: Mapped[str]
    telegram_id: Mapped[str]
    role: Mapped[str]
    viewed_at: Mapped[timestamp]
