from dagger.models.user import User
from dagger.schemas.user import UserCreate, UserUpdate
from dagger.services.base import ServiceBase


class UserService(ServiceBase[User, UserCreate, UserUpdate]):
    ...


user = UserService(User)
