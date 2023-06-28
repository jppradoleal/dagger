FROM python:3.10

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry

RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "-m", "dagger.main"]
