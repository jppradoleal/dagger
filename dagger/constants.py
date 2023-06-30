from os import getenv

ENV = getenv("ENV")
DATABASE_URL = getenv("DATABASE_URL")
ACCESS_TOKEN_EXPIRES_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRES_MINUTES"))
SECRET_KEY = getenv("SECRET_KEY")
API_V1_URL = getenv("API_V1_URL")
