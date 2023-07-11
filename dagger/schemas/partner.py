from datetime import datetime
from typing import Optional, Tuple, TypeVar

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConstrainedFloat, conlist, validator
from shapely.geometry import mapping, shape


class Latitude(ConstrainedFloat):
    ge = -90
    le = 90


class Longitude(ConstrainedFloat):
    ge = -180
    le = 180


PolygonCoordinates = TypeVar(
    "PolygonCoordinates",
    bound=conlist(conlist(Tuple[Latitude, Longitude], min_items=3), min_items=1),
)

MultiPolygonCoordinates = TypeVar(
    "MultiPolygonCoordinates", bound=conlist(PolygonCoordinates, min_items=1)
)


class BaseGeometry(BaseModel):
    @property
    def wkt_shape(self):
        return shape(self.dict()).wkt


class MultiPolygonGeometry(BaseGeometry):
    type: str = "MultiPolygon"
    coordinates: MultiPolygonCoordinates


class PointGeometry(BaseGeometry):
    type: str = "Point"
    coordinates: Tuple[Latitude, Longitude]


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
    updated_at: Optional[datetime]

    @validator("coverage_area", "address", pre=True)
    def format_shape_data(cls, value):
        return mapping(to_shape(value))

    class Config:
        orm_mode = True
