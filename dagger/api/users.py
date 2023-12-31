from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dagger import models, schemas, services
from dagger.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.user.User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(
        deps.get_current_active_superuser
    ),  # noqa: F401
):
    users = services.user.all(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.user.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserCreate,
):
    user = services.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken"
        )

    user = services.user.create(db, obj_in=user_in)

    return user


@router.get("/me", response_model=schemas.user.User)
def read_user_me(current_user: models.User = Depends(deps.get_current_active_user)):
    return current_user


@router.get("/{user_id}", response_model=schemas.user.User)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(
        deps.get_current_active_superuser
    ),  # noqa: F401
):
    user = services.user.get(db, id=user_id)

    return user
