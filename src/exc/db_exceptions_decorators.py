import functools
import logging
from collections.abc import Callable
from typing import TypeVar

from typing_extensions import ParamSpec

from exc.exc import ArqueaError, ResourceError

P = ParamSpec("P")
T = TypeVar("T")

regex_detail = r"\nDETAIL:  (.*?).$"

logger = logging.getLogger(__name__)


def db_catch_exception(resource: str) -> T:
    def inner_db_catch_exception(run_func: Callable[P, T]) -> Callable[P, T]:
        """This function implements a decorator to catch and handle the exceptions that are thrown in
        the methods of the crud modules.
        """

        @functools.wraps(run_func)
        def wrapper(*args, **kwargs):
            try:
                return run_func(*args, **kwargs)
            except ArqueaError as error:
                raise error from error
            except Exception as error:
                _resource = _retrieve_resource(args)
                raise ResourceError(_resource, str(error)) from error

        def _retrieve_resource(args: tuple) -> str:
            return (
                args[0].resource
                if args
                and hasattr(args[0], "__class__")
                and "SqlAlchemyCrudFacade" in str(args[0].__class__.__mro__)
                else resource
            )

        return wrapper

    return inner_db_catch_exception
