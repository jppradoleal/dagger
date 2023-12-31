from fastapi import status
from fastapi.testclient import TestClient

from dagger import models
from dagger.api import deps
from dagger.main import private_app


def test_create_duplicate_user(client: TestClient, create_user):
    user = create_user("jose@gmail.com", "password")
    response = client.post(
        "/api/users", json={"email": user.email, "password": "jose123"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_user(client: TestClient, create_user):
    users: list[models.User] = [
        create_user("maria@gmail.com", "123"),
        create_user("joao@gmail.com", "123"),
    ]

    user_jose = create_user("jose@gmail.com", "123", is_superuser=True)

    private_app.dependency_overrides[deps.get_current_user] = lambda: user_jose

    response = client.get("/api/users")

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()

    assert len(data) > 0

    emails = [user["email"] for user in data]

    for user in users:
        assert user.email in emails


def test_get_user_unauthorized(client: TestClient, create_user):
    create_user("maria@gmail.com", "123"),
    create_user("joao@gmail.com", "123"),

    user_not_jose = create_user("josue@gmail.com", "123", is_superuser=False)

    private_app.dependency_overrides[deps.get_current_user] = lambda: user_not_jose

    response = client.get("/api/users")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me(client: TestClient, create_user):
    user_jose = create_user("jose@gmail.com", "123")
    private_app.dependency_overrides[deps.get_current_user] = lambda: user_jose
    response = client.get("/api/users/me")

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()

    assert data["id"] == user_jose.id
