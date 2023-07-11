from typing import List

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from dagger import models, schemas, services
from dagger.api import deps

router = APIRouter()


@router.post("/", response_model=schemas.partner.Partner)
def create_partner(
    partner_in: schemas.partner.PartnerCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    partner = services.partner.create(db, obj_in=partner_in)
    return partner


# Get
@router.get("/", response_model=List[schemas.partner.Partner])
def list_partners(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    partners = services.partner.all(db, skip=skip, limit=limit)
    return partners


# Get by geographical position
@router.get("/search", response_model=List[schemas.partner.Partner])
def search_partner_by_geographical_position(
    lat: float,
    lng: float,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
) -> List[schemas.partner.Partner]:
    partners = services.partner.search_partner_by_geographical_position(
        db, lat=lat, lng=lng, skip=skip, limit=limit
    )
    return partners
