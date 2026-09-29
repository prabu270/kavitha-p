import os

os.environ[
    "DATABASE_URL"
] = "sqlite:///./test_pocketsmart.db"

os.environ[
    "AI_ENABLED"
] = "false"

os.environ[
    "SECRET_KEY"
] = "test-secret-key"


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_user():

    email = "tester@example.com"

    register_response = client.post(
        "/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": "password123",
        },
    )

    if register_response.status_code not in (
        201,
        409,
    ):

        raise AssertionError(
            register_response.text
        )


    login_response = client.post(
        "/login",
        json={
            "email": email,
            "password": "password123",
        },
    )

    assert (
        login_response.status_code
        == 200
    )


def test_health():

    response = client.get(
        "/health"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()["status"]
        == "ok"
    )


def test_registration_and_login():

    email = (
        "unique-user@example.com"
    )

    response = client.post(
        "/register",
        json={
            "email": email,
            "full_name": "Unique User",
            "password": "password123",
        },
    )

    assert (
        response.status_code
        == 201
    )


    response = client.post(
        "/login",
        json={
            "email": email,
            "password": "password123",
        },
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        "access_token"
        in response.json()
    )


def test_home_planner():

    create_test_user()

    response = client.post(
        "/generate-home",
        json={
            "budget": 25000,

            "room_type":
                "Living Room",

            "style":
                "Modern",

            "items": [
                {
                    "category":
                        "Lighting",

                    "quantity": 2,
                }
            ],
        },
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data["planner"]
        == "home"
    )

    assert (
        data["ai_generated"]
        is False
    )


def test_party_planner():

    create_test_user()

    response = client.post(
        "/generate-party",
        json={
            "budget": 30000,

            "guest_count": 25,

            "event_type":
                "Birthday",

            "venue":
                "Community Hall",

            "city":
                "Coimbatore",
        },
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()["planner"]
        == "party"
    )


def test_jewelry_planner():

    create_test_user()

    response = client.post(
        "/generate-jewelry",
        data={
            "budget": "10000",

            "occasion":
                "Wedding",

            "style":
                "Elegant",

            "outfit_color":
                "Pink",

            "metal_preference":
                "Gold-tone",
        },
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.json()["planner"]
        == "jewelry"
    )


def test_history():

    create_test_user()

    response = client.get(
        "/history"
    )

    assert (
        response.status_code
        == 200
    )

    assert isinstance(
        response.json(),
        list,
    )


def test_protected_route_without_login():

    client.post(
        "/logout"
    )

    response = client.post(
        "/generate-home",
        json={
            "budget": 10000,

            "room_type":
                "Bedroom",

            "style":
                "Modern",

            "items": [
                {
                    "category":
                        "Lighting",

                    "quantity": 1,
                }
            ],
        },
    )

    assert (
        response.status_code
        == 401
    )