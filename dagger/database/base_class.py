from sqlalchemy import BigInteger
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    id: BigInteger
    __name__: str

    __table_args__ = {"schema": "public"}

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
