import logging
from enum import StrEnum
from typing import Any

from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute, Load, RelationshipProperty, joinedload, selectinload
from sqlalchemy.sql.elements import BinaryExpression, ColumnElement, and_, or_

from conf.conf_types import FilterOperator

logger = logging.getLogger(__name__)


class Direction(StrEnum):
    ASC = "asc"
    DESC = "desc"


def _backward_compatible_value_for_like_and_ilike(value: str) -> str:
    """Add % if not in value to be backward compatible.

    Args:
        value (str): The value to filter.

    Returns:
        Either the unmodified value if a percent sign is present, the value wrapped in % otherwise to preserve
        current behavior.
    """
    if "%" not in value:
        value = f"%{value}%"
    return value


orm_operator_transformer = {
    "neq": lambda value: ("__ne__", value),
    "gt": lambda value: ("__gt__", value),
    "gte": lambda value: ("__ge__", value),
    "in": lambda value: ("in_", value),
    "isnull": lambda value: ("is_", None) if value is True else ("is_not", None),
    "isempty": lambda value: ("__eq__", "") if value is True else ("__ne__", ""),
    "lt": lambda value: ("__lt__", value),
    "lte": lambda value: ("__le__", value),
    "like": lambda value: ("like", _backward_compatible_value_for_like_and_ilike(value)),
    "ilike": lambda value: ("ilike", _backward_compatible_value_for_like_and_ilike(value)),
    # XXX(arthurio): Mysql excludes None values when using `in` or `not in` filters.
    "not": lambda value: ("is_not", value),
    "not_in": lambda value: ("not_in", value),
}
"""Operators à la Django.

Examples:
    my_datetime__gte
    count__lt
    name__isnull
    user_id__in
"""

orm_lazy_load = {"joined": joinedload, "selectin": selectinload}


def get_operator(filter_name: str, filter_value: Any) -> tuple[str, str, Any]:
    operator = "__eq__"
    if "__" in filter_name:
        filter_name, operator = filter_name.split("__")
        operator, filter_value = orm_operator_transformer[operator](filter_value)
    return operator, filter_name, filter_value


def get_column_criteria(model: DeclarativeBase, filter_name: str, filter_value: Any) -> BinaryExpression:
    operator, field_name, field_value = get_operator(filter_name=filter_name, filter_value=filter_value)
    model_field = getattr(model, field_name)
    return getattr(model_field, operator)(field_value)


def get_join_column_criteria(model: DeclarativeBase, filter_name: str,
                             filter_value: Any) -> tuple[BinaryExpression, Load]:
    join_column, filter_name = filter_name.split("___")
    lazy_load, column = get_lazy_load(model=model, column_name=join_column)
    criteria = get_column_criteria(model=column.property.mapper.class_,
                                   filter_name=filter_name,
                                   filter_value=filter_value)
    return criteria, lazy_load


def get_lazy_load(model: DeclarativeBase, column_name: str) -> tuple[Load, RelationshipProperty]:
    column = getattr(model, column_name, None)
    if isinstance(column, InstrumentedAttribute) and isinstance(column.property, RelationshipProperty):
        return orm_lazy_load[column.property.lazy](column), column
    raise AttributeError(f"Invalid filtering attribute: {column_name}")


def get_criteria(model: DeclarativeBase, filters: dict | list[tuple]) -> tuple[list[BinaryExpression], list[Load]]:
    """
        filters examples:
        >>> { "my_field__gt": 12, "my_other_field": "Tomato"}
        >>> { "my_field__in": [12,13], "my_other_field__not_in": ["Tomato", "Pepper"]}
        >>> { "my_join_column___join_field__in": [12,13]}
    """
    join_criteria = []
    criteria = []
    for filter_name, filter_value in (filters.items() if isinstance(filters, dict) else filters):
        if "___" in filter_name:
            column_criteria, column_load = get_join_column_criteria(model=model,
                                                                    filter_name=filter_name,
                                                                    filter_value=filter_value)
            criteria.append(column_criteria)
            join_criteria.append(column_load)
        else:
            criteria.append(get_column_criteria(model=model, filter_name=filter_name, filter_value=filter_value))
    return criteria, join_criteria


def get_filter_criteria(model: DeclarativeBase, filters: dict | list[tuple],
                        operator: FilterOperator) -> tuple[ColumnElement, list[Load]]:
    criteria, join_criteria = get_criteria(model=model, filters=filters)
    return (or_(*criteria) if operator is FilterOperator.OR else and_(*criteria)), join_criteria


def get_sort_criteria(model: DeclarativeBase, ordering_values: list[str]) -> list:
    """
        ordering_values examples:
        >>> ["-created_at"]
        >>> ["created_at", "updated_at"]
        >>> ["+created_at", "-name"]
    """
    sorting = []
    for sort_name in ordering_values:
        direction = Direction.DESC if sort_name.startswith("-") else Direction.ASC
        field_name = sort_name.replace("-", "").replace("+", "")
        try:
            order_by_field = getattr(model, field_name)
            sorting.append(getattr(order_by_field, direction)())
        except AttributeError:
            pass
    return sorting
