import abc
from typing import Any, Generic, TypeAlias, TypeVar

from conf.conf_types import FilterOperator
from conf.model import Pagination, PaginationFilter, SortBy
from sql.crud_repository_interface import CrudRepository, EntityIdT, EntityT

DtoIdType: TypeAlias = Any  # type of the ID that identifies a Data Transfer Object (DTO) (str, BaseModel, int, ...)
DtoIdT = TypeVar("DtoIdT", bound=DtoIdType)  # generic type to represent the IDs of the DTOs
DtoT = TypeVar("DtoT")  # generic type to represent the DTOs
DtoCreateT = TypeVar("DtoCreateT")  # generic type to represent the data used to create a DTO
DtoUpdateT = TypeVar("DtoUpdateT")  # generic type to represent the data to update of a DTO


class CrudFacade(abc.ABC, Generic[DtoIdT, DtoT, DtoCreateT, DtoUpdateT, EntityT, EntityIdT]):
    """An abstract class implementing a CRUD Facade for a given Data Transfer Object (DTO)

        DtoIdT: Type of ID of the DTO.
        DtoT: Type of DTO on which the facade performs operations.
        DtoCreateT: Type of data used to create a DTO.
        DtoUpdateT: Type of data to update of the DTO.
        EntityT: Type of the model that represents the DTO in the database.
        EntityIdT: Type of ID of the database model that represents the ID of the DTO.
    """

    _repository: CrudRepository[EntityT, EntityIdT]
    _default_pagination = PaginationFilter(offset=0, limit=0)

    def __init__(self, repository: CrudRepository[EntityT, EntityIdT], dto: type[DtoT]):
        self._repository = repository
        self._dto: type[DtoT] = dto

    @property
    def _model(self) -> type[EntityT]:
        return self._repository.model

    @property
    def resource(self) -> str:
        return self._repository.resource

    def create(self, data: DtoCreateT) -> DtoT:
        """Creates a new entity from the given DTO

        Args:
            data (DtoCreateT): The DTO to create the entity from

        Returns:
            DtoT: The DTO of the created entity

        Raises:
            ResourceAlreadyExistsError: If already exist an entry in the database with the same key.
        """
        entity = self._mapping_from_dto_create_to_entity(data=data)
        self._repository.add(entity=entity)
        return self._mapping_from_entity_to_dto(entity=entity)

    def create_paginated(self, data: list[DtoCreateT]) -> Pagination[DtoT]:
        """Creates new entities from the given DTOs

        Args:
            data (list[DtoCreateT]): The DTOs to create the entities from.

        Returns:
            PaginationModel[DtoT]: A paginated list of DTOs

        Raises:
            ResourceAlreadyExistsError: If already exist an entry in the database with the same key.
        """
        entities = [self._mapping_from_dto_create_to_entity(data=entry) for entry in data]
        self._repository.add_all(entities=entities)
        data = [self._mapping_from_entity_to_dto(entity=entity) for entity in entities]
        return Pagination(data=data, total_count=len(entities), offset=0, limit=len(data))

    def get(self, key: DtoIdT) -> DtoT:
        """Returns the DTO of the entity that matches the given primary key

        Args:
            key (DtoT): The primary key of the entity to be returned

        Returns:
            DtoT: The DTO of the entity that matches the given primary key

        Raises:
            ResourceMissingError: If no entity matches the given primary key
        """
        entity_key = self._mapping_key_from_dto_to_entity(key=key)
        entity = self._repository.get_by_key_or_fail(key=entity_key)
        return self._mapping_from_entity_to_dto(entity=entity)

    def get_one_by(self, **kwargs: Any) -> DtoT:
        """Returns the DTO of the entity that matches the given primary key

        Args:
            **kwargs (Any): The criteria to be used to filter the DTOs

        Returns:
            DtoT: The DTO of the entity that matches the given primary key

        Raises:
            ResourceMissingError: If no entity matches the given primary key
        """
        entity = self._repository.get_one_by_or_fail(**kwargs)
        return self._mapping_from_entity_to_dto(entity=entity)

    def get_latest_by(self, **kwargs: Any) -> DtoT:
        """Returns the latest DTO of the entity that matches the given primary key

        Args:
            **kwargs (Any): The criteria to be used to filter the DTOs

        Returns:
            DtoT: The DTO of the entity that matches the given primary key

        Raises:
            ResourceMissingError: If no entity matches the given primary key
        """
        raise NotImplementedError

    def get_list(self,
                 pagination: PaginationFilter | None = None,
                 sort_by: SortBy | None = None,
                 operator: FilterOperator | None = None,
                 mandatory: dict | list[tuple] | None = None,
                 **kwargs: Any) -> tuple[list[DtoT], int]:
        """Returns a list of DTOs

        Args:
            pagination (optional, PaginationFilter): Pagination filter to apply to the query
            sort_by (optional, SortBy): Columns order to apply to the query
            operator (FilterOperator): Logical operator to apply to the filters
            mandatory (dict): Mandatory criteria to apply after filter the DTOs
            **kwargs (Any): The criteria to be used to filter the DTOs

        Returns:
            list[DtoT]: Tuple of a list of DTOs and the total of DTOs that meet the criteria
        """
        _pagination = pagination or PaginationFilter(offset=0, limit=0)
        entities, total = self._repository.get_and_count(offset=_pagination.offset,
                                                         limit=_pagination.limit,
                                                         sort_by=sort_by.sort if sort_by else None,
                                                         operator=operator,
                                                         mandatory=mandatory,
                                                         **kwargs)
        data = [self._mapping_from_entity_to_dto(entity=entity) for entity in entities]
        return data, total

    def get_paginated(self,
                      pagination: PaginationFilter | None = None,
                      sort_by: SortBy | None = None,
                      operator: FilterOperator | None = None,
                      mandatory: dict | list[tuple] | None = None,
                      **kwargs: Any) -> Pagination[DtoT]:
        """Returns a paginated list of DTOs

        Args:
            pagination (optional, PaginationFilter): Pagination filter to apply to the query
            sort_by (optional, SortBy): Columns order to apply to the query
            operator (FilterOperator): Logical operator to apply to the filters
            mandatory (dict): Mandatory criteria to apply after filter the DTOs
            **kwargs (Any): The criteria to be used to filter the DTOs

        Returns:
            PaginationModel[DtoT]: A paginated list of DTOs
        """
        _pagination = pagination or self._default_pagination
        data, total = self.get_list(pagination=_pagination,
                                    sort_by=sort_by,
                                    operator=operator,
                                    mandatory=mandatory,
                                    **kwargs)
        return Pagination(data=data, total_count=total, **_pagination.model_dump())

    def update(self, key: DtoIdT, data: DtoUpdateT) -> DtoT:
        """Updates the entity that matches the given DTO

        Args:
            key (DtoT): The primary key of the entity to be updated
            data (DtoUpdateT): The DTO to update the entity from

        Returns:
            DtoT: The DTO of the updated entity

        Raises:
            ResourceMissingError: If no entity matches the given primary key
        """
        entity_key = self._mapping_key_from_dto_to_entity(key=key)
        entity_data = self._mapping_from_dto_update_to_dict(data=data)
        entity_updated = self._repository.update_by_key(key=entity_key, data=entity_data)
        return self._mapping_from_entity_to_dto(entity=entity_updated)

    def update_one_by(self, data: DtoUpdateT, **kwargs: Any) -> DtoT:
        """Updates the entity that matches the given criteria

        Args:
            **kwargs (Any): The criteria to be used to filter the DTOs
            data (DtoUpdateT): The DTO to update the entity from

        Returns:
            DtoT: The DTO of the updated entity

        Raises:
            ResourceAlreadyExistsError: If no DTO matches the given criteria
            ResourceUniqueError: if multiple DTOs match the given criteria
        """
        entity_data = self._mapping_from_dto_update_to_dict(data=data)
        entity = self._repository.update_one_by_or_fail(data=entity_data, **kwargs)
        return self._mapping_from_entity_to_dto(entity=entity)

    def delete(self, key: DtoIdT) -> DtoT:
        """Deletes the entity that matches the given primary key

        Args:
            key (DtoIdT): The primary key of the entity to be deleted

        Returns:
            DtoT: The DTO of the deleted entity
        """
        entity_key = self._mapping_key_from_dto_to_entity(key=key)
        dto = self.get(key=entity_key)
        self._repository.delete_by_key(key=key)
        return dto

    def delete_one_by(self, **kwargs: Any) -> DtoT:
        """Deletes the entity that matches the given criteria

        Args:
            **kwargs (Any): The criteria to be used to filter the DTOs

        Returns:
            DtoT: The DTO of the deleted entity
        """
        dto = self.get_one_by(**kwargs)
        self._repository.delete_by(**kwargs)
        return dto

    def delete_list(self, operator: FilterOperator | None = None, **kwargs: Any) -> list[DtoT]:
        """Delete all the DTOs that match the given criteria

        Args:
            operator (FilterOperator): Logical operator to apply to the filters
            **kwargs (Any): The criteria to be used to filter the DTOs

        Returns:
            PaginationModel[DtoT]: A list of DTOs
        """
        dtos, _ = self.get_list(operator=operator, **kwargs)
        self._repository.delete_by(**kwargs)
        return dtos

    def delete_paginated(self, operator: FilterOperator | None = None, **kwargs: Any) -> Pagination[DtoT]:
        """Delete all the DTOs that match the given criteria

        Args:
            operator (FilterOperator): Logical operator to apply to the filters
            **kwargs (Any): The criteria to be used to filter the DTOs

        Returns:
            PaginationModel[DtoT]: A paginated list of DTOs
        """
        dtos = self.get_paginated(pagination=PaginationFilter(limit=0, offset=0), operator=operator, **kwargs)
        self._repository.delete_by(**kwargs)
        return dtos

    def _mapping_key_from_dto_to_entity(self, key: DtoIdT) -> EntityIdT:
        return key

    @staticmethod
    def _mapping_key_from_entity_to_dto(key: EntityIdT) -> DtoIdT:
        return key

    @abc.abstractmethod
    def _mapping_from_dto_create_to_entity(self, data: DtoCreateT) -> EntityT:
        raise NotImplementedError

    @abc.abstractmethod
    def _mapping_from_dto_update_to_dict(self, data: DtoUpdateT) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def _mapping_from_dto_to_entity(self, dto: DtoT) -> EntityT:
        raise NotImplementedError

    @abc.abstractmethod
    def _mapping_from_entity_to_dto(self, entity: EntityT) -> DtoT:
        raise NotImplementedError
