from typing import Any, TypeVar
from uuid import UUID, uuid4

from sqlalchemy import Select, delete, func, select, update
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session

from conf.conf_types import FilterOperator
from conf.db import Base
from exc.exc import ResourceMissingError, ResourceUniqueError
from sql.crud_filter_sqlalchemy import get_filter_criteria, get_sort_criteria
from sql.crud_repository_interface import CrudRepository
from utils.date_utils import utc_now

EntitySqlSqlAlchemyT = TypeVar("EntitySqlSqlAlchemyT", bound=Base)
EntityIdSqlAlchemyT = TypeVar("EntityIdSqlAlchemyT", bound=UUID)


class SqlAlchemyRepository(CrudRepository[EntitySqlSqlAlchemyT, EntityIdSqlAlchemyT]):
    """SQLAlchemy repository implementation"""

    def __init__(self, resource: str, model: type[EntitySqlSqlAlchemyT], session: Session):
        super().__init__(resource=resource, model=model)
        self.session: Session = session

    def add(self, entity: EntitySqlSqlAlchemyT) -> None:
        self.session.add(entity)
        self.flush(entity=entity)

    def add_all(self, entities: list[EntitySqlSqlAlchemyT]) -> None:
        self.session.add_all(entities)
        self.session.flush()

    def get_all(
        self,
        offset: int = 0,
        limit: int = 15,
        sort_by: list[str] | None = None,
        operator: FilterOperator | None = None,
        mandatory: dict | list[tuple] | None = None,
        **kwargs: Any,
    ) -> list[EntitySqlSqlAlchemyT]:
        query = self._get_query(
            mandatory=mandatory, filters=kwargs, operator=operator, offset=offset, limit=limit, sort_by=sort_by
        )
        return list((self.session.scalars(query)).all())

    def count_by(
        self, operator: FilterOperator | None = None, mandatory: dict | list[tuple] | None = None, **kwargs: Any
    ) -> int:
        query = self._get_filter_query(mandatory=mandatory, filters=kwargs, operator=operator)
        return self.session.scalar(select(func.count()).select_from(query.subquery()))

    def get_and_count(
        self,
        offset: int = 0,
        limit: int = 15,
        sort_by: list[str] | None = None,
        operator: FilterOperator | None = None,
        mandatory: dict | list[tuple] | None = None,
        **kwargs: Any,
    ) -> tuple[list[EntitySqlSqlAlchemyT], int]:
        query = self._get_filter_query(mandatory=mandatory, filters=kwargs, operator=operator)
        query_paginated = self._apply_paginated_query(query=query, offset=offset, limit=limit, sort_by=sort_by)
        entities = list((self.session.scalars(query_paginated)).all())
        count = self.session.scalar(select(func.count()).select_from(query.subquery()))
        return entities, count

    def get_by_key(self, key: EntityIdSqlAlchemyT) -> EntitySqlSqlAlchemyT | None:
        return self.session.get(self.model, key)

    def get_by_key_or_fail(self, key: EntityIdSqlAlchemyT) -> EntitySqlSqlAlchemyT:
        if entity := self.get_by_key(key=key):
            return entity
        raise (self.resource, f"Resource with id '{key}' not found")

    def get_one_by(
        self,
        offset: int = 0,
        limit: int = 15,
        sort_by: list[str] | None = None,
        operator: FilterOperator | None = None,
        mandatory: dict | list[tuple] | None = None,
        **kwargs: Any,
    ) -> EntitySqlSqlAlchemyT | None:
        query = self._get_query(
            mandatory=mandatory,
            filters=kwargs,
            operator=operator or FilterOperator.AND,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
        )
        return self.session.scalar(query)

    def get_one_by_or_fail(
        self,
        offset: int = 0,
        limit: int = 15,
        sort_by: list[str] | None = None,
        operator: FilterOperator | None = None,
        mandatory: dict | list[tuple] | None = None,
        **kwargs: Any,
    ) -> EntitySqlSqlAlchemyT:
        query = self._get_query(
            mandatory=mandatory,
            filters=kwargs,
            operator=operator or FilterOperator.AND,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
        )
        try:
            return (self.session.scalars(query)).one()
        except MultipleResultsFound as exc:
            raise ResourceUniqueError(self.resource, f"Multiple entities found: {kwargs}") from exc
        except NoResultFound as exc:
            raise ResourceMissingError(self.resource, f"Resource not found: {kwargs}") from exc

    def update(self, entity: EntitySqlSqlAlchemyT) -> EntitySqlSqlAlchemyT:
        kwargs = self.entity_to_dict(entity=entity, exclude=["id"])
        return self.update_by_key(key=entity.id, data=kwargs)

    def update_by_key(self, key: EntityIdSqlAlchemyT, data: dict) -> EntitySqlSqlAlchemyT:
        kwargs = {**data, "updated_at": utc_now()}
        query = update(self.model).where(self.model.id == key).values(**kwargs)
        self.session.scalar(query.execution_options(synchronize_session="fetch"))
        self.flush()
        return self.get_by_key_or_fail(key=key)

    def update_one_by_or_fail(self, data: dict, **kwargs: Any) -> EntitySqlSqlAlchemyT:
        entity = self.get_one_by_or_fail(**kwargs)
        return self.update_by_key(key=entity.id, data=data)

    def delete(self, entity: EntitySqlSqlAlchemyT) -> None:
        self.session.delete(entity)
        self.flush()

    def delete_by_key(self, key: EntityIdSqlAlchemyT) -> None:
        query = delete(self.model).where(self.model.id == key)
        self.session.execute(query)
        self.flush()

    def delete_by(self, **kwargs) -> None:
        criteria, _join_criteria = get_filter_criteria(model=self.model, filters=kwargs, operator=FilterOperator.AND)
        query = delete(self.model).options(*_join_criteria).where(criteria)
        self.session.execute(query)
        self.flush()

    def delete_all(self, entities: list[EntitySqlSqlAlchemyT]) -> None:
        for entity in entities:
            self.session.delete(entity)
        self.flush()

    def delete_all_by_keys(self, keys: list[EntityIdSqlAlchemyT]) -> None:
        query = delete(self.model).where(self.model.id.in_(keys))
        self.session.execute(query)
        self.flush()

    def prune(self) -> None:
        query = delete(self.model)
        self.session.execute(query)
        self.flush()

    def flush(self, entity: EntitySqlSqlAlchemyT | None = None) -> None:
        self.session.flush()
        if entity:
            self.session.refresh(entity)

    def _get_query(
        self,
        mandatory: dict | list[tuple] | None = None,
        filters: dict | list[tuple] | None = None,
        operator: FilterOperator | None = None,
        offset: int | None = None,
        limit: int | None = None,
        sort_by: list[str] | None = None,
    ) -> Select:
        query = self._get_filter_query(mandatory=mandatory, filters=filters, operator=operator)
        return self._apply_paginated_query(query=query, offset=offset, limit=limit, sort_by=sort_by)

    def _get_filter_query(
        self,
        mandatory: dict | list[tuple] | None = None,
        filters: dict | list[tuple] | None = None,
        operator: FilterOperator | None = None,
    ) -> Select:
        _mandatory, _mandatory_join_criteria = get_filter_criteria(
            model=self.model, filters=mandatory or {}, operator=operator or FilterOperator.OR
        )
        _filter, _join_criteria = get_filter_criteria(
            model=self.model, filters=filters or {}, operator=operator or FilterOperator.OR
        )
        _options = set(_mandatory_join_criteria + _join_criteria)
        return select(self.model).options(*_options).filter(_filter).filter(_mandatory)

    def _apply_paginated_query(
        self, query: Select, offset: int | None = None, limit: int | None = None, sort_by: list[str] | None = None
    ) -> Select:
        _offset = None if offset and offset < 0 else offset
        _limit = None if limit and limit < 1 else limit
        _sort = get_sort_criteria(model=self.model, ordering_values=sort_by or [])
        if _offset:
            query = query.offset(_offset)
        if _limit:
            query = query.limit(_limit)
        if _sort:
            query = query.order_by(*_sort)
        return query

    def entity_to_dict(self, entity: EntitySqlSqlAlchemyT, exclude: list | None) -> dict:
        return {
            column.name: entity.__getattribute__(column.name)
            for column in self.model.__table__.columns  # type:ignore
            if column.name not in (exclude or [])
        }

    def new_entity(self, data: dict) -> EntitySqlSqlAlchemyT:
        current_datetime = utc_now()
        for field, value in [("id", uuid4()), ("created_at", current_datetime), ("updated_at", current_datetime)]:
            if not data.get(field):
                data[field] = value
        return self.model(**data)
