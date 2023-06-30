from typing import Any, Dict

from sqlalchemy.orm import Session

from dagger.models.user import User
from dagger.schemas.user import UserCreate, UserUpdate
from dagger.services.base import ServiceBase
from dagger.services.security import security


class UserService(ServiceBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str):
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=security.get_password_hash(obj_in.password),
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: UserUpdate | Dict[str, Any]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if update_data["password"]:
            hashed_password = security.get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def authenticate(self, db: Session, *, email: str, password: str):
        user = self.get_by_email(db, email=email)

        if not user:
            return None

        if not security.verify_password(password, user.hashed_password):
            return None

        return user


user = UserService(User)
