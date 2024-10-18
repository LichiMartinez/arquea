from enum import StrEnum
from typing import TypeAlias

from pydantic import BaseModel, Field

from conf.model import AppDtoIdType, AppModel, BaseFilter, UpdateBaseModel, optional
from utils.date_utils import UTCDatetime

__all__ = [
    "DtoIdType",
    "User",
    "UserData",
    "UserCreate",
    "UserUpdate",
    "UserFilter",
    "UserCreateData",
]

DtoIdType: TypeAlias = AppDtoIdType


class UserRole(StrEnum):
    ADMIN = "admin"
    EMPLOYEE = "employee"


class UserFilter(BaseFilter):
    id__in: list[DtoIdType] | None = Field(None, description="Search an ID list")

    # provider_code: str | None = Field(None, description="Filter by provider code")
    # provider_code__in: list[str] | None = Field(None, description="Search a provider code list")
    # user_id: UUID | None = Field(None, description="Filter by user ID")
    # user_id__in: list[UUID] | None = Field(None, description="Search a user ID list")
    # status: str | None = Field(None, description="Filter by status")
    # status__in: list[str] | None = Field(None, description="Search a status list")
    # state: str | None = Field(None, description="Filter by state")
    # state__in: list[str] | None = Field(None, description="Search a state list")
    # provider_reference: str | None = Field(None, description="Search a provider reference")
    # provider_reference__in: list[str] | None = Field(None, description="Search a provider reference list")
    # provider_reference__isnull: bool | None = Field(None, description="Filter if provider_reference is null")
    # contract_type: str | None = Field(None, description="Search a contract type")
    # expiration_date: UTCDatetime | None = Field(None, description="Filter by expiration_date")
    # expiration_date__isnull: bool | None = Field(None, description="Filter if expiration_date is null")
    # expiration_date__gt: UTCDatetime | None = Field(None, description="Filter by expiration_date")
    # expiration_date__lt: UTCDatetime | None = Field(None, description="Filter by expiration_date")
    # active_date: UTCDatetime | None = Field(None, description="Filter by active_date")
    # active_date__isnull: bool | None = Field(None, description="Filter if active_date is null")
    # active_date__gt: UTCDatetime | None = Field(None, description="Filter by active_date")
    # active_date__lt: UTCDatetime | None = Field(None, description="Filter by active_date")
    # pause_start_date: UTCDatetime | None = Field(None, description="Filter by pause_start_date")
    # pause_start_date__isnull: bool | None = Field(None, description="Filter if pause_start_date is null")
    # pause_start_date__gt: UTCDatetime | None = Field(None, description="Filter by pause_start_date")
    # pause_start_date__lt: UTCDatetime | None = Field(None, description="Filter by pause_start_date")
    # pause_end_date: UTCDatetime | None = Field(None, description="Filter by pause_end_date")
    # pause_end_date__isnull: bool | None = Field(None, description="Filter if pause_end_date is null")
    # pause_end_date__gt: UTCDatetime | None = Field(None, description="Filter by pause_end_date")
    # pause_end_date__lt: UTCDatetime | None = Field(None, description="Filter by pause_end_date")
    # cancellation_date: UTCDatetime | None = Field(None, description="Filter by cancellation_date")
    # cancellation_date__isnull: bool | None = Field(None, description="Filter if cancellation_date is null")
    # cancellation_date__gt: UTCDatetime | None = Field(None, description="Filter by cancellation_date")
    # cancellation_date__lt: UTCDatetime | None = Field(None, description="Filter by cancellation_date")


class UserTelegramData(BaseModel):
    telegram_id: str = Field(description="Telegram ID")


class UserCreateData(BaseModel):
    first_name: str = Field(description="User first name")
    last_name: str = Field(description="User last name")
    role: str = Field(description="User role")


class UserCreate(UserCreateData, UserTelegramData):
    viewed_at: UTCDatetime = Field(description="Legacy field")


class UserData(UserCreateData, extra="allow"): ...


OptionalUserData = optional(UserData)


class User(OptionalUserData, AppModel):
    viewed_at: UTCDatetime = Field(description="Legacy field")


class UserUpdate(UpdateBaseModel, OptionalUserData):
    viewed_at: UTCDatetime | None = Field(None, description="Legacy field")
