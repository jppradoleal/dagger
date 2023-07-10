from sqlalchemy import BigInteger, Boolean, Column, Integer, String

from dagger.database.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True
    )
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
