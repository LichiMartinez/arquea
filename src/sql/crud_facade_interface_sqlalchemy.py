import logging
from abc import ABC
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic_core._pydantic_core import ValidationError

from conf.conf_types import FilterOperator
from conf.model import Pagination, PaginationFilter, SortBy
from exc.db_exceptions_decorators import db_catch_exception
from sql.crud_facade_interface import CrudFacade, DtoIdT
from sql.crud_repository_interface_sqlalchemy import (
    SqlAlchemyRepository,
    EntityIdSqlAlchemyT,
    EntitySqlSqlAlchemyT,
)

DtoSqlSqlAlchemyT = TypeVar("DtoSqlSqlAlchemyT", bound=BaseModel)
DtoCreateSqlSqlAlchemyT = TypeVar("DtoCreateSqlSqlAlchemyT", bound=BaseModel)
DtoUpdateSqlSqlAlchemyT = TypeVar("DtoUpdateSqlSqlAlchemyT", bound=BaseModel)


class SqlAlchemyCrudFacade(CrudFacade[DtoIdT, DtoSqlSqlAlchemyT, DtoCreateSqlSqlAlchemyT, DtoUpdateSqlSqlAlchemyT,
                                           EntitySqlSqlAlchemyT, EntityIdSqlAlchemyT], ABC):
    _resource = "SqlAlchemyCrudFacade"
    _repository: SqlAlchemyRepository[EntitySqlSqlAlchemyT, EntityIdSqlAlchemyT]
    _dto: type[DtoSqlSqlAlchemyT]

    _default_pagination = PaginationFilter(offset=0, limit=1000000)
    _default_sort_by = SortBy(sort=["+code", "+slug", "-created_at", "-updated_at"])
    _sort_latest = SortBy(sort=["-created_at", "-updated_at"])

    def __init__(self, repository: SqlAlchemyRepository[EntitySqlSqlAlchemyT, EntityIdSqlAlchemyT],
                 dto: type[DtoSqlSqlAlchemyT]):
        super().__init__(repository=repository, dto=dto)

    @property
    def repository(self) -> SqlAlchemyRepository[EntitySqlSqlAlchemyT, EntityIdSqlAlchemyT]:
        return self._repository

    @db_catch_exception(resource=_resource)
    def create_raw(self, data: dict) -> dict:
        entity = self._repository.new_entity(data=data)
        self._repository.add(entity=entity)
        return self._mapping_from_entity_to_dict(entity=entity)

    @db_catch_exception(resource=_resource)
    def create_raw_paginated(self, data: list[dict]) -> Pagination[dict]:
        entities = [self._repository.new_entity(data=entry) for entry in data]
        self._repository.add_all(entities=entities)
        data = [self._mapping_from_entity_to_dict(entity=entity) for entity in entities]
        return Pagination[dict](data=data, total_count=len(entities), offset=0, limit=len(data))

    @db_catch_exception(resource=_resource)
    def create(self, data: DtoCreateSqlSqlAlchemyT) -> DtoSqlSqlAlchemyT:
        entity = self._mapping_from_dto_create_to_entity(data=data)
        self._repository.add(entity=entity)
        return self._mapping_from_entity_to_dto(entity=entity)

    @db_catch_exception(resource=_resource)
    def create_paginated(self, data: list[DtoCreateSqlSqlAlchemyT]) -> Pagination[DtoSqlSqlAlchemyT]:
        entities = [self._mapping_from_dto_create_to_entity(data=entry) for entry in data]
        self._repository.add_all(entities=entities)
        data = [self._mapping_from_entity_to_dto(entity=entity) for entity in entities]
        return Pagination[self._dto](data=data, total_count=len(entities), offset=0, limit=len(data))

    @db_catch_exception(resource=_resource)
    def get_raw_list(self,
                           pagination: PaginationFilter | None = None,
                           sort_by: SortBy | None = None,
                           operator: FilterOperator | None = None,
                           mandatory: dict | list[tuple] | None = None,
                           **kwargs: Any) -> tuple[list, int]:
        _pagination = pagination or self._default_pagination
        _sort_by = self._default_sort_by if not sort_by or not sort_by.sort else sort_by
        entities, total = self._repository.get_and_count(offset=_pagination.offset,
                                                               limit=_pagination.limit,
                                                               sort_by=_sort_by.sort if _sort_by else None,
                                                               operator=operator,
                                                               mandatory=mandatory,
                                                               **kwargs)
        data = [self._mapping_from_entity_to_dict(entity=entity) for entity in entities]
        return data, total

    @db_catch_exception(resource=_resource)
    def get_raw_paginated(self,
                                pagination: PaginationFilter | None = None,
                                sort_by: SortBy | None = None,
                                operator: FilterOperator | None = None,
                                mandatory: dict | list[tuple] | None = None,
                                **kwargs: Any) -> Pagination[dict]:
        _pagination = pagination or self._default_pagination
        data, total = self.get_raw_list(pagination=_pagination,
                                              sort_by=sort_by,
                                              operator=operator,
                                              mandatory=mandatory,
                                              **kwargs)
        return Pagination[dict](data=data, total_count=total, **_pagination.model_dump())

    @db_catch_exception(resource=_resource)
    def get(self, key: DtoIdT) -> DtoSqlSqlAlchemyT:
        entity_key = self._mapping_key_from_dto_to_entity(key=key)
        entity = self._repository.get_by_key_or_fail(key=entity_key)
        return self._mapping_from_entity_to_dto(entity=entity)

    @db_catch_exception(resource=_resource)
    def get_one_by(self, **kwargs: Any) -> DtoSqlSqlAlchemyT:
        entity = self._repository.get_one_by_or_fail(**kwargs)
        return self._mapping_from_entity_to_dto(entity=entity)

    @db_catch_exception(resource=_resource)
    def get_latest_by(self, **kwargs: Any) -> DtoSqlSqlAlchemyT:
        entity = self._repository.get_one_by_or_fail(sort_by=self._sort_latest.sort, limit=1, **kwargs)
        return self._mapping_from_entity_to_dto(entity=entity)

    @db_catch_exception(resource=_resource)
    def get_list(self,
                       pagination: PaginationFilter | None = None,
                       sort_by: SortBy | None = None,
                       operator: FilterOperator | None = None,
                       mandatory: dict | list[tuple] | None = None,
                       **kwargs: Any) -> tuple[list[DtoSqlSqlAlchemyT], int]:
        _pagination = pagination or self._default_pagination
        _sort_by = self._default_sort_by if not sort_by or not sort_by.sort else sort_by
        entities, total = self._repository.get_and_count(offset=_pagination.offset,
                                                               limit=_pagination.limit,
                                                               sort_by=_sort_by.sort if _sort_by else None,
                                                               operator=operator,
                                                               mandatory=mandatory,
                                                               **kwargs)
        data = [dto for dto in (self._mapping_from_entity_to_dto_or_none(entity=entity) for entity in entities) if dto]
        return data, total

    @db_catch_exception(resource=_resource)
    def get_paginated(self,
                            pagination: PaginationFilter | None = None,
                            sort_by: SortBy | None = None,
                            operator: FilterOperator | None = None,
                            mandatory: dict | list[tuple] | None = None,
                            **kwargs: Any) -> Pagination[DtoSqlSqlAlchemyT]:
        _pagination = pagination or self._default_pagination
        data, total = self.get_list(pagination=_pagination,
                                          sort_by=sort_by,
                                          operator=operator,
                                          mandatory=mandatory,
                                          **kwargs)
        return Pagination[self._dto](data=data, total_count=total, **_pagination.model_dump())

    @db_catch_exception(resource=_resource)
    def update(self, key: DtoIdT, data: DtoUpdateSqlSqlAlchemyT) -> DtoSqlSqlAlchemyT:
        entity_key = self._mapping_key_from_dto_to_entity(key=key)
        entity_data = self._mapping_from_dto_update_to_dict(data=data)
        entity_updated = self._repository.update_by_key(key=entity_key, data=entity_data)
        return self._mapping_from_entity_to_dto(entity=entity_updated)

    @db_catch_exception(resource=_resource)
    def update_one_by(self, data: DtoUpdateSqlSqlAlchemyT, **kwargs: Any) -> DtoSqlSqlAlchemyT:
        entity_data = self._mapping_from_dto_update_to_dict(data=data)
        entity = self._repository.update_one_by_or_fail(data=entity_data, **kwargs)
        return self._mapping_from_entity_to_dto(entity=entity)

    @db_catch_exception(resource=_resource)
    def delete(self, key: DtoIdT) -> DtoSqlSqlAlchemyT:
        dto = self.get(key=key)
        self._repository.delete_by_key(key=key)
        return dto

    @db_catch_exception(resource=_resource)
    def delete_one_by(self, **kwargs: Any) -> DtoSqlSqlAlchemyT:
        dto = self.get_one_by(**kwargs)
        self._repository.delete_by(**kwargs)
        return dto

    @db_catch_exception(resource=_resource)
    def delete_paginated(self,
                               operator: FilterOperator | None = None,
                               **kwargs: Any) -> Pagination[DtoSqlSqlAlchemyT]:
        dtos = self.get_paginated(pagination=PaginationFilter(limit=0, offset=0), operator=operator, **kwargs)
        self._repository.delete_by(**kwargs)
        dtos.limit = max(dtos.limit, dtos.total_count)
        return dtos

    def _mapping_from_dto_create_to_entity(self, data: DtoCreateSqlSqlAlchemyT) -> EntitySqlSqlAlchemyT:
        return self._repository.new_entity(data=data.model_dump())

    def _mapping_from_dto_update_to_dict(self, data: DtoUpdateSqlSqlAlchemyT) -> dict:
        return data.model_dump(exclude_unset=True)

    def _mapping_from_dto_to_entity(self, dto: DtoSqlSqlAlchemyT) -> EntitySqlSqlAlchemyT:
        return self._model(**dto.model_dump())

    def _mapping_from_entity_to_dto(self, entity: EntitySqlSqlAlchemyT) -> DtoSqlSqlAlchemyT:
        return self._dto.model_validate(entity.__dict__)

    def _mapping_from_entity_to_dto_or_none(self, entity: EntitySqlSqlAlchemyT) -> DtoSqlSqlAlchemyT | None:
        try:
            return self._mapping_from_entity_to_dto(entity=entity)
        except ValidationError as error:
            logging.warning(f"mapping error:\n   - entity: {entity}\n   - error: {error}")
            return None

    @staticmethod
    def _mapping_from_entity_to_dict(entity: EntitySqlSqlAlchemyT) -> dict:
        return {key: value for key, value in entity.__dict__.items() if key not in ["_sa_instance_state"]}
