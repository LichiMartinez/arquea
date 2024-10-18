import inspect
from copy import deepcopy
from decimal import Decimal
from types import UnionType
from typing import Annotated, Any, Generic, TypeAlias, TypeVar

from pydantic import UUID4, BaseModel, ConfigDict, Field, PlainSerializer, create_model, field_validator
from pydantic._internal._model_construction import ModelMetaclass as PydanticModelMetaclass
from pydantic.fields import FieldInfo

from conf.conf_types import FilterOperator
from utils.date_utils import UTCDatetime

DataT = TypeVar("DataT")
BaseModelT = TypeVar("BaseModelT", bound=BaseModel)

AppDtoIdType: TypeAlias = UUID4

ForJsonDecimalToFloat = Annotated[Decimal, PlainSerializer(lambda x: float(x), return_type=float, when_used="json")]


class AppModel(BaseModel):
    id: UUID4 | None = None
    created_at: UTCDatetime | None = None
    updated_at: UTCDatetime | None = None
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class UpdateBaseModel(BaseModel):

    def model_dump(self, *args, exclude_unset: bool = True, **kwargs) -> dict:
        """Generate a dictionary representation of the model, whose keys will be in camelCase format.

        The parameter `exclude_unset` is set as True by default in order to update only those fields that
        have been set by the user.
        In this way, it is easy to distinguish the fields that the user has indicated as null from those that
        the user has not set and are null because they are optional.
        """
        return super().model_dump(exclude_unset=exclude_unset, *args, **kwargs)  # noqa: B026


ExcludeUnsetBaseModel: TypeAlias = UpdateBaseModel


class BaseFilterNoOperator(BaseModel, extra="forbid"):
    """Base model for the searching filters"""

    @field_validator("*", mode="before")
    def validate_string(cls, value: Any) -> Any:  # noqa : N805
        if not value:
            return value
        return (value if isinstance(value, str) else
                [str(v) if v else v for v in value] if isinstance(value, list) else str(value))

    @field_validator("*")
    def empty_list_to_none(cls, value: Any) -> Any:  # noqa : N805
        return value if value != [] else None

    def model_dump(self, *args, **kwargs) -> dict:
        kwargs["exclude_unset"] = True
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class BaseFilter(BaseFilterNoOperator):
    """Base model for the searching filters"""

    operator: FilterOperator | None = Field(None, description="Logical operator to apply to the filters")


class PaginationFilter(BaseModel):
    """Pagination filter"""

    offset: int = Field(0, ge=0, description="The page number")
    limit: int = Field(1000000, ge=0, description="The number of items per page")

    @field_validator("offset", "limit", mode="before")
    @classmethod
    def none_as_zero(cls, v: int) -> int:
        return 0 if v is None else v


class SortBy(BaseModel):
    sort: list[str] = Field([],
                            description="Sorting field ascending/descending order (+/-)",
                            examples=["-createdAt", "+updatedAt"])


class Pagination(PaginationFilter, Generic[DataT]):
    """Generic Pagination model for the Data Transfer Objects"""

    total_count: int = Field(description="The total number of items")
    data: list[DataT] = Field(description="The list of items")


def optional(cls: type[BaseModelT]) -> type[BaseModelT]:
    """Decorator to define all the BaseModel fields as Optional and to set their default value to None"""

    def is_model(field: Any) -> bool:
        return inspect.isclass(field) and issubclass(field, BaseModel)

    def set_optional_field(field: FieldInfo) -> tuple[UnionType, FieldInfo]:
        _field = deepcopy(field)
        _field.default = None
        if is_model(_field.annotation):
            return dec(_cls=_field.annotation, _fields=_field.annotation.model_fields) | None, _field  # type: ignore
        return _field.annotation | None, _field

    def dec(_cls: PydanticModelMetaclass, _fields: dict) -> type[BaseModelT]:
        fields_dict = {field_name: set_optional_field(field=field) for field_name, field in _fields.items()}
        return create_model(_cls.__name__, __module__=_cls.__module__, **fields_dict)

    if is_model(cls):
        return dec(_cls=cls, _fields=cls.model_fields)

    return cls
