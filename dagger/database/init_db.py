from sqlalchemy.orm import Session

from dagger import constants, schemas, services


def init_db(db: Session):
    user = services.user.get_by_email(db, email=constants.SUPERUSER_EMAIL)
    if not user:
        user_in = schemas.user.UserCreate(
            email=constants.SUPERUSER_EMAIL,
            password=constants.SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = services.user.create(db, user_in)
