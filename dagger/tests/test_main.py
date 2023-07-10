from fastapi import status


def test_app(client):
    response = client.get("/docs")

    assert response.status_code == status.HTTP_200_OK
