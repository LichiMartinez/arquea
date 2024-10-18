import abc
from typing import Any, Generic, TypeAlias, TypeVar

from conf.conf_types import FilterOperator

EntityIdType: TypeAlias = Any  # type of the ID that identifies a database model (dict, DeclarativeBase, Document, ...)
EntityIdT = TypeVar("EntityIdT", bound=EntityIdType)  # generic type to represent the IDs of the entities
EntityT = TypeVar("EntityT")  # generic type to represent the entities


class CrudRepository(abc.ABC, Generic[EntityT, EntityIdT]):
    """Abstract Repository Class. Provides an interface for entity repositories to implement.

    EntityT: Type of the database model.
    EntityIdT: Type of the ID of the database model.
    """

    def __init__(self, resource: str, model: type[EntityT]):
        self._resource: str = resource
        self._model: type[EntityT] = model

    @property
    def resource(self) -> str:
        return self._resource

    @property
    def model(self) -> type[EntityT]:
        return self._model

    @abc.abstractmethod
    def add(self, entity: EntityT) -> None:
        """Adds the indicated entity to the repository

        Args:
            entity (EntityT): The entity to be added

        Returns:
            None

        Raises:
            ResourceAlreadyExistsError: If already exist an entry in the database with the same key.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_all(self, entities: list[EntityT]) -> None:
        """Adds a list of entities into the repository

        Args:
            entities (list[EntityT]): The list of entities

        Raises:
            ResourceAlreadyExistsError: If any of the entities already exist an entry in the database with the same key.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count_by(
        self, operator: FilterOperator | None = None, mandatory: dict | list[tuple] | None = None, **kwargs: Any
    ) -> int:
        """Returns the number of entities that match the given criteria

        Args:
            operator (FilterOperator): Logical operator to apply to the filters
            mandatory (dict): Mandatory criteria to apply after filter the entities
            **kwargs (Any): The criteria to be used to filter the entities

        Returns:
            int: The number of entities that match the given criteria
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all(
        self,
        offset: int = 0,
        limit: int = 15,
        sort: list[str] | None = None,
        operator: FilterOperator | None = None,
        mandatory: dict | list[tuple] | None = None,
        **kwargs: Any,
    ) -> list[EntityT]:
        """Returns a paginated list of entities that match the provided criteria

        Args:
            offset (int): The page number to be returned
            limit (int): The number of entities per page
            sort (list[str]): Order by criteria: -column for descending, +column for ascending
            operator (FilterOperator): Logical operator to apply to the filters
            mandatory (dict): Mandatory criteria to apply after filter the entities
            **kwargs (Any): The criteria to be used to filter the entities

        Returns:
            list[EntityT]: The list of entities that match the given criteria
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_and_count(
        self,
        offset: int = 0,
        limit: int = 15,
        sort_by: list[str] | None = None,
        operator: FilterOperator | None = None,
        mandatory: dict | list[tuple] | None = None,
        **kwargs: Any,
    ) -> tuple[list[EntityT], int]:
        """Returns a list of paginated entities as well as the count of entities that match the given criteria

        Args:
            offset (int): The page number to be returned
            limit (int): The number of entities per page
            sort_by (optional, list[str]): Order by criteria: -column for descending, +column for ascending
            operator (FilterOperator): Logical operator to apply to the filters
            mandatory (dict): Mandatory criteria to apply after filter the entities
            **kwargs (Any): The criteria to be used to filter the entities

        Returns:
            Tuple[list[EntityT], int]: The list of entities that match the given criteria and the total number of
                entities
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_key(self, key: EntityIdT) -> EntityT | None:
        """Returns the entity that matches the given primary key

        Args:
            key (EntityIdT): The primary key of the entity to be returned

        Returns:
            Optional[EntityT]: The entity that matches the given primary key or null if no entity matches the given
                primary key
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_key_or_fail(self, key: EntityIdT) -> EntityT:
        """Returns the entity that matches the given primary key

        Args:
            key (EntityIdT): The primary key of the entity to be returned

        Returns:
            EntityT: The entity that matches the given primary key

        Raises:
            ResourceMissingError: If no entity matches the given primary key
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_one_by(
        self,
        offset: int = 0,
        limit: int = 15,
        sort_by: list[str] | None = None,
        operator: FilterOperator | None = None,
        mandatory: dict | list[tuple] | None = None,
        **kwargs: Any,
    ) -> EntityT | None:
        """Returns the entity that matches the given criteria

        Args:
            offset (int): The page number to be returned
            limit (int): The number of entities per page
            sort_by (optional, list[str]): Order by criteria: -column for descending, +column for ascending
            operator (FilterOperator): Logical operator to apply to the filters
            mandatory (dict): Mandatory criteria to apply after filter the entities
            **kwargs (Any): The criteria to be used to filter the entities

        Returns:
            Optional[EntityT]: The entity that matches the given criteria or null if no entity or multiple entities
                entity matches the given criteria
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_one_by_or_fail(
        self,
        offset: int = 0,
        limit: int = 15,
        sort_by: list[str] | None = None,
        operator: FilterOperator | None = None,
        mandatory: dict | list[tuple] | None = None,
        **kwargs: Any,
    ) -> EntityT:
        """Returns the entity that matches the given criteria

        Args:
            offset (int): The page number to be returned
            limit (int): The number of entities per page
            sort_by (optional, list[str]): Order by criteria: -column for descending, +column for ascending
            operator (FilterOperator): Logical operator to apply to the filters
            mandatory (dict): Mandatory criteria to apply after filter the entities
            **kwargs (Any): The criteria to be used to filter the entities

        Returns:
            EntityT: The entity that matches the given criteria

        Raises:
            ResourceMissingError: if multiple entities match the given criteria
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, entity: EntityT) -> EntityT:
        """Update the entity that matches the given primary key

        Args:
            entity (EntityT): The updated entity

        Returns:
            entity (EntityT): The updated entity

        Raises:
            ResourceMissingError: If no entity matches the given primary key
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_by_key(self, key: EntityIdT, data: dict) -> EntityT:
        """Update the entity that matches the given primary key

        Args:
            key (EntityIdT): The primary key of the entity to be updated
            data (dict): The data to update

        Returns:
            entity (EntityT): The updated entity

        Raises:
            ResourceMissingError: If no entity matches the given primary key
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_one_by_or_fail(self, data: dict, **kwargs: Any) -> EntityT:
        """Update the entity that matches the given criteria

        Args:
            data (dict): The data to update
            **kwargs (Any): The criteria to be used to filter the entity

        Returns:
            entity (EntityT): The updated entity

        Raises:
            ResourceAlreadyExistsError: If no entity matches the given criteria
            ResourceUniqueError: If multiple entities match the given criteria
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, entity: EntityT) -> None:
        """Deletes the given entity from the repository

        Args:
            entity (EntityT): The entity to be deleted

        Returns:
            None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by_key(self, key: EntityIdT) -> None:
        """Deletes the entity that matches the given primary key from the repository

        Args:
            key (EntityIdT): The primary key of the entity to be deleted

        Returns:
            None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by(self, **kwargs) -> None:
        """Deletes the entity that matches the given primary key from the repository

        Args:
            **kwargs (Any): The criteria to be used to filter the entity

        Returns:
            None
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self, entities: list[EntityT]) -> None:
        """Deletes the given entities from the repository

        Args:
            entities (list[EntityT]): The entities to be deleted

        Returns:
            None
        """
        raise NotImplementedError

    def delete_all_by_keys(self, keys: list[EntityIdT]) -> None:
        """Deletes the entities with the given keys from the repository

        Args:
            keys (list[EntityIdT]): The keys to be deleted

        Returns:
            None
        """
        raise NotImplementedError

    def prune(self) -> None:
        """Deletes all the entities from the repository

        Returns:
            None
        """
        raise NotImplementedError
