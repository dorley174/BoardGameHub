"""Tests for the users API."""
from __future__ import annotations
from fastapi.testclient import TestClient


def create_user(client: TestClient, username: str = "alice"):
    """Helper to create a user through the API."""
    return client.post("/users", json={"username": username})


def test_create_user_success(client: TestClient) -> None:
    response = create_user(client, "alice")

    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "alice"}


def test_create_user_rejects_duplicate_username(client: TestClient) -> None:
    first_response = create_user(client, "alice")
    second_response = create_user(client, "alice")

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Username already exists."}


def test_create_user_rejects_duplicate_username_case_insensitive(
    client: TestClient,
) -> None:
    first_response = create_user(client, "Alice")
    second_response = create_user(client, "alice")

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Username already exists."}


def test_create_user_validates_username_format(client: TestClient) -> None:
    response = create_user(client, "  !bad username  ")

    assert response.status_code == 422


def test_get_user_by_id_success(client: TestClient) -> None:
    created_user = create_user(client, "alice").json()
    response = client.get(f"/users/{created_user['id']}")

    assert response.status_code == 200
    assert response.json() == created_user


def test_get_user_by_id_returns_404_for_missing_user(
    client: TestClient,
) -> None:
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}


def test_search_user_by_username_success(client: TestClient) -> None:
    created_user = create_user(client, "alice").json()
    response = client.get("/users/search", params={"username": "alice"})

    assert response.status_code == 200
    assert response.json() == created_user


def test_search_user_by_username_is_case_insensitive(
    client: TestClient,
) -> None:
    created_user = create_user(client, "Alice").json()
    response = client.get("/users/search", params={"username": "alice"})

    assert response.status_code == 200
    assert response.json() == created_user


def test_search_user_by_username_returns_404_for_missing_user(
    client: TestClient,
) -> None:
    response = client.get("/users/search", params={"username": "ghost"})

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}
