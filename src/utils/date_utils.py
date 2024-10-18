from datetime import datetime, UTC
from typing import Annotated
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import AfterValidator
from pydantic.json_schema import WithJsonSchema


def utc_now() -> datetime:
    """
    Generate a timezone aware utcnow.
    """
    return datetime.now(UTC)

def ensure_tzinfo(date_value: datetime | None) -> datetime | None:
    # if TZ isn't provided, we assume UTC, but you can do w/e you need
    if date_value is None:
        return None

    if date_value.tzinfo is None:
        return date_value.replace(tzinfo=UTC)
    # else we convert to utc
    return date_value.astimezone(UTC)


UTCDatetime = Annotated[datetime,
                        AfterValidator(lambda dt: ensure_tzinfo(dt)),
                        PlainSerializer(lambda dt: dt.isoformat(), when_used="json", return_type=str),
                        WithJsonSchema({"type": "datetime"}, mode="serialization"),]
