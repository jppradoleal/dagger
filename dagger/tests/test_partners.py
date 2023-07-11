from fastapi import status
from fastapi.testclient import TestClient

from dagger.api import deps
from dagger.main import private_app


def test_create_partner(client: TestClient, create_user):
    user_jose = create_user("jose@gmail.com", "123")

    private_app.dependency_overrides[deps.get_current_user] = lambda: user_jose

    response = client.post(
        "/api/partners",
        json={
            "trading_name": "Bodega do Ze",
            "owner_name": "Ze",
            "document": "4546236587",
            "address": {"type": "Point", "coordinates": [-23.309909, -45.965029]},
            "coverage_area": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-45.98708, -23.313928],
                            [-45.983422, -23.293525],
                            [-45.948181, -23.290125],
                            [-45.939989, -23.309136],
                            [-45.964926, -23.326551],
                            [-45.98708, -23.313928],
                        ]
                    ]
                ],
            },
        },
    )

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()

    assert data["id"], data["is_active"]


def test_get_all_partners(client: TestClient, create_partner):
    partners = [
        create_partner(
            trading_name="Bodega do Zé", owner_name="Zé", document="12345678910"
        ),
        create_partner(
            trading_name="Barzinho do Robson",
            owner_name="Robson",
            document="12345678911",
        ),
        create_partner(
            trading_name="Adega do Aderbal",
            owner_name="Aderbal",
            document="12345678912",
        ),
    ]

    response = client.get("/api/partners")

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()

    ids = [partner["id"] for partner in data]

    for partner in partners:
        assert partner.id in ids, partner.is_active


def test_search_partner_by_geographical_position(client: TestClient, create_partner):
    partners = [
        create_partner(
            trading_name="Bodega do Zé", owner_name="Zé", document="12345678910"
        ),
        create_partner(
            trading_name="Barzinho do Robson",
            owner_name="Robson",
            document="12345678911",
            coverage_coordinates=[
                [
                    [
                        [-45.996457, -23.310064],
                        [-45.988523, -23.302541],
                        [-45.972963, -23.3096],
                        [-45.980228, -23.325314],
                        [-45.995478, -23.323717],
                        [-45.996457, -23.310064],
                    ],
                    [],
                ]
            ],
        ),
        create_partner(
            trading_name="Adega do Aderbal",
            owner_name="Aderbal",
            document="12345678912",
            coverage_coordinates=[
                [
                    [
                        [-46.00908, -23.30893],
                        [-45.999755, -23.303933],
                        [-45.997127, -23.313516],
                        [-46.006401, -23.317483],
                        [-46.011398, -23.313928],
                        [-46.00908, -23.30893],
                    ],
                    [],
                ]
            ],
        ),
    ]

    response = client.get(
        "/api/partners/search", params={"lat": -23.312021, "lng": -45.979764}
    )

    assert response.status_code == status.HTTP_200_OK, response.text

    data = response.json()

    ids = [partner["id"] for partner in data]

    partner_out_of_range = partners.pop()

    assert partner_out_of_range.id not in ids

    for partner in partners:
        assert partner.id in ids, partner.is_active
