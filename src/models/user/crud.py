from sqlalchemy.orm import Session

from conf.model import AppDtoIdType
from models.user import db_model, model
from sql.crud_facade_interface_sqlalchemy import SqlAlchemyCrudFacade
from sql.crud_repository_interface_sqlalchemy import SqlAlchemyRepository
from sql.database import get_db

__all__ = ["UserCrudRepository", "UserCrudFacade"]


class UserCrudRepository(SqlAlchemyRepository[db_model.DBUser, db_model.UserEntityIdType]):
    def __init__(self, session: Session):
        super().__init__(resource="user", model=db_model.DBUser, session=session)


class UserCrudFacade(
    SqlAlchemyCrudFacade[
        AppDtoIdType, model.User, model.UserCreate, model.UserUpdate, db_model.DBUser, db_model.UserEntityIdType
    ]
):
    _resource = "UserCrudFacade"

    def __init__(self, repository: UserCrudRepository):
        super().__init__(repository=repository, dto=model.User)


def get_user_facade() -> UserCrudFacade:
    with get_db() as session:
        return UserCrudFacade(repository=UserCrudRepository(session=session))

