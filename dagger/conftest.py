from typing import Callable

from fastapi.testclient import TestClient
from pytest import fixture
from shapely import MultiPolygon, Point
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import func, select

from dagger import models
from dagger.api import deps
from dagger.database.base import Base
from dagger.main import app, private_app

SQLALCHEMY_DATABASE_URL = "sqlite://"


@fixture(scope="session")
def db_stuff():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        execution_options={"schema_translate_map": {"public": None}},
        # echo=True,
    )

    def load_spatialite(dbapi_conn, connection_record):
        dbapi_conn.enable_load_extension(True)
        dbapi_conn.execute("SELECT load_extension('mod_spatialite');")

    listen(engine, "connect", load_spatialite)

    with engine.connect() as conn:
        try:
            conn.execute(select([func.InitSpatialMetaData()]))
        except Exception:
            pass

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, TestingSessionLocal


@fixture
def session(db_stuff):
    engine, TestingSessionLocal = db_stuff

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    private_app.dependency_overrides[deps.get_db] = override_get_db

    yield TestClient(app)


@fixture
def create_user(session: Session) -> Callable[[str, str, bool, bool], models.User]:
    def create_user(email, hashed_password, *, is_active=True, is_superuser=False):
        user_in = models.User(
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        session.add(user_in)
        session.commit()
        session.refresh(user_in)

        return user_in

    return create_user


jacarei_centro_coverage = [
    [
        [
            [-45.98708, -23.313928],
            [-45.983422, -23.293525],
            [-45.948181, -23.290125],
            [-45.939989, -23.309136],
            [-45.964926, -23.326551],
            [-45.98708, -23.313928],
        ],
        [],
    ]
]


@fixture
def create_partner(
    session: Session,
) -> Callable[[str, str, str, list, list], models.Partner]:
    def create_partner(
        *,
        trading_name,
        owner_name,
        document,
        address_coordinate=[-23.309909, -45.965029],
        coverage_coordinates=jacarei_centro_coverage
    ):
        partner_in = models.Partner(
            trading_name=trading_name,
            owner_name=owner_name,
            document=document,
            address=Point(address_coordinate).wkt,
            coverage_area=MultiPolygon(coverage_coordinates).wkt,
        )

        session.add(partner_in)
        session.commit()
        session.refresh(partner_in)

        return partner_in

    return create_partner
