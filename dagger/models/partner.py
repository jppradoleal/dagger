from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String
from sqlalchemy.sql import func

from dagger.database.base_class import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(BigInteger, primary_key=True, index=True)
    trading_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    document = Column(String, nullable=False, unique=True)
    coverage_area = Column(Geometry("MULTIPOLYGON"), nullable=False)
    address = Column(Geometry("POINT"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
