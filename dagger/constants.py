from os import getenv

ENV = getenv("ENV", "dev")
DATABASE_URL = getenv("DATABASE_URL", "sqlite://")
ACCESS_TOKEN_EXPIRES_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRES_MINUTES", 60))
SECRET_KEY = getenv("SECRET_KEY", "dagger")
API_V1_URL = getenv("API_V1_URL", "/api")
