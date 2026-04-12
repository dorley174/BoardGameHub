"""Tests for the games API."""
from __future__ import annotations

from fastapi.testclient import TestClient


def create_user(client: TestClient, username: str = "alice"):
    """Helper to create a user through the API."""
    return client.post("/users", json={"userName": username})


def add_game(
    client: TestClient,
    user_id: int,
    game_name: str = "Catan",
    is_available: bool = True,
):
    """Helper to add a game to a user's collection."""
    return client.post(
        f"/users/{user_id}/games",
        json={"gameName": game_name, "isAvailable": is_available},
    )


def test_add_game_to_user_success(client: TestClient) -> None:
    user = create_user(client, "alice").json()

    response = add_game(client, user["userId"], "Catan")

    assert response.status_code == 201
    assert response.json() == {
        "userGameId": 1,
        "userId": 1,
        "gameId": 1,
        "gameName": "Catan",
        "isAvailable": True,
    }


def test_add_game_reuses_existing_game_record_for_other_user(
    client: TestClient,
) -> None:
    alice = create_user(client, "alice").json()
    bob = create_user(client, "bob").json()

    first_response = add_game(client, alice["userId"], "Catan")
    second_response = add_game(client, bob["userId"], "  catan  ")

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["gameId"] == 1
    assert second_response.json()["gameId"] == 1
    assert second_response.json()["userGameId"] == 2
    assert second_response.json()["gameName"] == "Catan"


def test_add_game_rejects_duplicate_game_for_same_user(
    client: TestClient,
) -> None:
    user = create_user(client, "alice").json()

    first_response = add_game(client, user["userId"], "Catan")
    second_response = add_game(client, user["userId"], "catan")

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Game already exists in user's collection.",
    }


def test_add_game_returns_404_for_missing_user(client: TestClient) -> None:
    response = add_game(client, 999, "Catan")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}


def test_add_game_validates_non_empty_name(client: TestClient) -> None:
    user = create_user(client, "alice").json()

    response = add_game(client, user["userId"], "   ")

    assert response.status_code == 422


def test_list_user_games_success(client: TestClient) -> None:
    alice = create_user(client, "alice").json()
    bob = create_user(client, "bob").json()

    catan = add_game(client, alice["userId"], "Catan").json()
    pandemic = add_game(
        client,
        alice["userId"],
        "Pandemic",
        is_available=False,
    ).json()
    add_game(client, bob["userId"], "Carcassonne")

    response = client.get(f"/users/{alice['userId']}/games")

    assert response.status_code == 200
    assert response.json() == [catan, pandemic]


def test_list_user_games_returns_empty_list(client: TestClient) -> None:
    user = create_user(client, "alice").json()

    response = client.get(f"/users/{user['userId']}/games")

    assert response.status_code == 200
    assert response.json() == []


def test_list_user_games_returns_404_for_missing_user(
    client: TestClient,
) -> None:
    response = client.get("/users/999/games")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}


def test_update_user_game_status_success(client: TestClient) -> None:
    user = create_user(client, "alice").json()
    created_game = add_game(client, user["userId"], "Catan").json()

    response = client.patch(
        f"/users/{user['userId']}/games/{created_game['userGameId']}/status",
        json={"isAvailable": False},
    )

    assert response.status_code == 200
    assert response.json() == {
        "userGameId": 1,
        "userId": 1,
        "gameId": 1,
        "gameName": "Catan",
        "isAvailable": False,
    }


def test_update_user_game_status_returns_404_for_missing_game(
    client: TestClient,
) -> None:
    user = create_user(client, "alice").json()

    response = client.patch(
        f"/users/{user['userId']}/games/999/status",
        json={"isAvailable": False},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Game not found in user's collection.",
    }


def test_remove_user_game_success(client: TestClient) -> None:
    user = create_user(client, "alice").json()
    created_game = add_game(client, user["userId"], "Catan").json()

    response = client.delete(
        f"/users/{user['userId']}/games/{created_game['userGameId']}"
    )
    games_response = client.get(f"/users/{user['userId']}/games")

    assert response.status_code == 204
    assert response.text == ""
    assert games_response.status_code == 200
    assert games_response.json() == []


def test_remove_user_game_returns_404_for_missing_game(
    client: TestClient,
) -> None:
    user = create_user(client, "alice").json()

    response = client.delete(f"/users/{user['userId']}/games/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Game not found in user's collection.",
    }
