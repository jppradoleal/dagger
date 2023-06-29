from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel


class MultiPolygonGeometry(BaseModel):
    type: str = "MultiPolygon"
    coordinates: List[List[List[List[float]]]]


class PointGeometry(BaseModel):
    type: str = "Point"
    coordinates: Annotated[List[float], 2]


class PartnerBase(BaseModel):
    trading_name: str
    owner_name: str
    coverage_area: MultiPolygonGeometry
    address: PointGeometry


class PartnerCreate(PartnerBase):
    document: str


class PartnerUpdate(PartnerBase):
    trading_name: Optional[str] = None
    coverage_area: Optional[MultiPolygonGeometry] = None
    address: Optional[PointGeometry] = None


class Partner(PartnerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
