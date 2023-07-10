from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import func, select

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
        execution_options={"schema_translate_map": {"public": None}}
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
