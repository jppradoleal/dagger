FROM python:3.10 as base
LABEL org.opencontainers.image.source="https://github.com/jppradoleal/dagger"
WORKDIR /app
EXPOSE 8000

FROM python:3.10 as build
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry
RUN poetry install
COPY . .
RUN ["poetry", "run", "alembic", "upgrade", "head"]
CMD ["poetry", "run", "python", "-m", "dagger.main"]
