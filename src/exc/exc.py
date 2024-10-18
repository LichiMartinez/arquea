from dataclasses import asdict, dataclass


@dataclass
class ArqueaError(Exception):
    """
    A base exception for all things Arquea, you shouldn't be really raising this.
    Instead, inherit from and override its default values.
    """

    _type = "undefined_error"

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def type(self) -> str:
        return self._type

    @property
    def detail(self) -> dict:
        return {"type": self._type}

    def __str__(self):
        return self.__repr__()

    def to_dict(self) -> dict:
        """
        Convert this error into a justifiable dict.
        """
        return asdict(self)


@dataclass
class ResourceError(ArqueaError):
    resource: str
    params: str

    @property
    def detail(self) -> dict:
        return {"type": self._type, "content": {"resource": self.resource, "params": self.params}}


@dataclass
class ResourceUniqueError(ResourceError):
    """
    Multiple resources found when only one was expected.
    """

    _type = "resource_unique"


@dataclass
class ResourceMissingError(ResourceError):
    """
    A resource doesn't exist.
    """

    _type = "resource_missing"
