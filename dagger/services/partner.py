from geoalchemy2 import WKTElement, functions
from sqlalchemy.orm import Session

from dagger.models.partner import Partner
from dagger.schemas.partner import PartnerCreate, PartnerUpdate
from dagger.services.base import ServiceBase


class PartnerService(ServiceBase[Partner, PartnerCreate, PartnerUpdate]):
    def create(self, db: Session, *, obj_in: PartnerCreate) -> Partner:
        db_obj = self.model(
            trading_name=obj_in.trading_name,
            owner_name=obj_in.owner_name,
            document=obj_in.document,
            coverage_area=obj_in.coverage_area.wkt_shape,
            address=obj_in.address.wkt_shape,
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def search_partner_by_geographical_position(
        self, db: Session, *, lat: float, lng: float, skip: int = 0, limit: int = 100
    ):
        partners = (
            db.query(self.model)
            .filter(
                functions.ST_Contains(
                    self.model.coverage_area, WKTElement(f"POINT({lng} {lat})")
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return partners


partner = PartnerService(Partner)
