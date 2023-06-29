from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dagger import schemas, services
from dagger.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def get_users(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100):
    users = services.user.get(db, skip, limit)
    return users
