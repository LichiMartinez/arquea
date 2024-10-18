from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def todict(obj: Any) -> dict[Any, Any]:
    """Return the object's dict excluding private attributes,
    sqlalchemy state and relationship attributes.
    """
    excl = ("_sa_adapter", "_sa_instance_state")
    return {k: v for k, v in vars(obj).items() if not k.startswith("_") and not any(hasattr(v, a) for a in excl)}


timestamp = Annotated[
    datetime, mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.UTC_TIMESTAMP())
]


class Base(DeclarativeBase):
    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default="uuid_generate_v4()")

    def __repr__(self):
        params = ", ".join(f"{k}={v}" for k, v in todict(self).items())
        return f"{self.__class__.__name__}({params})"
