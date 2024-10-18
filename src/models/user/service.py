from models.user.crud import get_user_facade
from models.user.model import UserCreate, User


class UserService():
    def __init__(self) -> None:
        self.facade = get_user_facade()
    
    def create(self, data: UserCreate) -> User:
        return self.facade.create(data=data)
