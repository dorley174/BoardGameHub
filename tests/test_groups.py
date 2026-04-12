from __future__ import annotations

from src.models import Game, User, UserGame


def create_user(session, username: str) -> User:
    user = User(userName=username)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_game(session, game_name: str) -> Game:
    game = Game(gameName=game_name)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


def give_game_to_user(session, user: User, game: Game, available: bool = True):
    user_game = UserGame(
        userId=user.userId,
        gameId=game.gameId,
        isAvailable=available,
    )
    session.add(user_game)
    session.commit()
    session.refresh(user_game)
    return user_game


def test_create_group_adds_creator_as_member(client, session):
    creator = create_user(session, "creator")

    response = client.post(
        "/groups",
        json={
            "groupName": "Friday Night",
            "creatorUserId": creator.userId,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["groupName"] == "Friday Night"
    assert data["creatorUserId"] == creator.userId

    group_id = data["groupId"]

    members_response = client.get(f"/groups/{group_id}/members")
    assert members_response.status_code == 200
    assert members_response.json() == [
        {
            "groupId": group_id,
            "userId": creator.userId,
            "userName": "creator",
        }
    ]


def test_creator_can_invite_member_by_username(client, session):
    creator = create_user(session, "creator")
    create_user(session, "alice")

    group_response = client.post(
        "/groups",
        json={
            "groupName": "Board Night",
            "creatorUserId": creator.userId,
        },
    )
    group_id = group_response.json()["groupId"]

    invite_response = client.post(
        f"/groups/{group_id}/members",
        json={
            "username": "alice",
            "invitedByUserId": creator.userId,
        },
    )

    assert invite_response.status_code == 201
    assert invite_response.json()["userName"] == "alice"

    members_response = client.get(f"/groups/{group_id}/members")
    members = members_response.json()
    assert {member["userName"] for member in members} == {"creator", "alice"}


def test_only_creator_can_invite(client, session):
    creator = create_user(session, "creator")
    bob = create_user(session, "bob")
    create_user(session, "alice")

    group_response = client.post(
        "/groups",
        json={
            "groupName": "Private Group",
            "creatorUserId": creator.userId,
        },
    )
    group_id = group_response.json()["groupId"]

    response = client.post(
        f"/groups/{group_id}/members",
        json={
            "username": "alice",
            "invitedByUserId": bob.userId,
        },
    )

    assert response.status_code == 403


def test_group_games_returns_collective_games(client, session):
    creator = create_user(session, "creator")
    alice = create_user(session, "alice")
    bob = create_user(session, "bob")
    outsider = create_user(session, "outsider")

    group_response = client.post(
        "/groups",
        json={
            "groupName": "Collection",
            "creatorUserId": creator.userId,
        },
    )
    group_id = group_response.json()["groupId"]

    client.post(
        f"/groups/{group_id}/members",
        json={
            "username": "alice",
            "invitedByUserId": creator.userId,
        },
    )
    client.post(
        f"/groups/{group_id}/members",
        json={
            "username": "bob",
            "invitedByUserId": creator.userId,
        },
    )

    chess = create_game(session, "Chess")
    catan = create_game(session, "Catan")
    gloomhaven = create_game(session, "Gloomhaven")

    give_game_to_user(session, alice, chess, available=True)
    give_game_to_user(session, bob, catan, available=False)
    give_game_to_user(session, outsider, gloomhaven, available=True)

    games_response = client.get(f"/groups/{group_id}/games")
    assert games_response.status_code == 200

    games = games_response.json()
    names = {item["gameName"] for item in games}
    assert names == {"Chess", "Catan"}
    assert all(item["userName"] in {"alice", "bob"} for item in games)
