"""CRUD helpers for the users, games, and groups slices."""
from __future__ import annotations

from sqlalchemy import func
from sqlmodel import Session, select

from .models import Game, Group, GroupMember, User, UserGame
from .schemas import GroupCreate, UserCreate, UserGameCreate, UserGameRead


def create_user(session: Session, user_in: UserCreate) -> User:
    """Persist a new user in the database."""
    existing_user = get_user_by_username(session, user_in.userName)
    if existing_user is not None:
        raise ValueError("Username already exists.")

    user = User(userName=user_in.userName)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> User | None:
    """Return a user by primary key."""
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    """Return a user by username, case-insensitively."""
    statement = select(User).where(
        func.lower(User.userName) == username.lower()
    )
    return session.exec(statement).first()


def get_game_by_name(session: Session, game_name: str) -> Game | None:
    """Return a game by title, case-insensitively."""
    statement = select(Game).where(
        func.lower(Game.gameName) == game_name.lower()
    )
    return session.exec(statement).first()


def get_user_game(
    session: Session,
    user_id: int,
    user_game_id: int,
) -> UserGame | None:
    """Return a game entry from a specific user's collection."""
    statement = select(UserGame).where(
        UserGame.userGameId == user_game_id,
        UserGame.userId == user_id,
    )
    return session.exec(statement).first()


def add_game_to_user(
    session: Session,
    user_id: int,
    game_in: UserGameCreate,
) -> UserGameRead:
    """Add a game to a user's collection."""
    if get_user(session, user_id) is None:
        raise LookupError("User not found.")

    game = get_game_by_name(session, game_in.gameName)
    if game is None:
        game = Game(gameName=game_in.gameName)
        session.add(game)
        session.flush()

    existing_user_game = session.exec(
        select(UserGame).where(
            UserGame.userId == user_id,
            UserGame.gameId == game.gameId,
        )
    ).first()
    if existing_user_game is not None:
        raise ValueError("Game already exists in user's collection.")

    user_game = UserGame(
        userId=user_id,
        gameId=game.gameId,
        isAvailable=game_in.isAvailable,
    )
    session.add(user_game)
    session.commit()
    session.refresh(user_game)
    return _build_user_game_read(user_game, game.gameName)


def list_user_games(session: Session, user_id: int) -> list[UserGameRead]:
    """Return all games owned by a user."""
    if get_user(session, user_id) is None:
        raise LookupError("User not found.")

    statement = (
        select(UserGame, Game)
        .join(Game, Game.gameId == UserGame.gameId)
        .where(UserGame.userId == user_id)
        .order_by(UserGame.userGameId)
    )
    user_games = session.exec(statement).all()
    return [
        _build_user_game_read(user_game, game.gameName)
        for user_game, game in user_games
    ]


def update_user_game_availability(
    session: Session,
    user_id: int,
    user_game_id: int,
    is_available: bool,
) -> UserGameRead:
    """Update a game's availability flag in a user's collection."""
    if get_user(session, user_id) is None:
        raise LookupError("User not found.")

    user_game = get_user_game(session, user_id, user_game_id)
    if user_game is None:
        raise LookupError("Game not found in user's collection.")

    user_game.isAvailable = is_available
    session.add(user_game)
    session.commit()
    session.refresh(user_game)

    game = session.get(Game, user_game.gameId)
    return _build_user_game_read(user_game, game.gameName)


def remove_game_from_user(
    session: Session,
    user_id: int,
    user_game_id: int,
) -> None:
    """Remove a game from a user's collection."""
    if get_user(session, user_id) is None:
        raise LookupError("User not found.")

    user_game = get_user_game(session, user_id, user_game_id)
    if user_game is None:
        raise LookupError("Game not found in user's collection.")

    game_id = user_game.gameId
    session.delete(user_game)
    session.flush()

    remaining_links = session.exec(
        select(func.count())
        .select_from(UserGame)
        .where(UserGame.gameId == game_id)
    ).one()
    if remaining_links == 0:
        game = session.get(Game, game_id)
        if game is not None:
            session.delete(game)

    session.commit()


def create_group(session: Session, group_in: GroupCreate) -> Group:
    """Create a new group."""
    group = Group(
        groupName=group_in.groupName,
        creatorUserId=group_in.creatorUserId,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def get_group(session: Session, group_id: int) -> Group | None:
    """Return a group by primary key."""
    return session.get(Group, group_id)


def add_group_member(
    session: Session,
    group_id: int,
    user_id: int,
) -> GroupMember:
    """Add a user to a group."""
    membership = GroupMember(userId=user_id, groupId=group_id)
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def get_group_member(
    session: Session,
    group_id: int,
    user_id: int,
) -> GroupMember | None:
    """Return a membership record if it exists."""
    statement = select(GroupMember).where(
        GroupMember.groupId == group_id,
        GroupMember.userId == user_id,
    )
    return session.exec(statement).first()


def list_group_members(session: Session, group_id: int) -> list[User]:
    """Return all users in a group."""
    statement = (
        select(User)
        .join(GroupMember, GroupMember.userId == User.userId)
        .where(GroupMember.groupId == group_id)
        .order_by(User.userName)
    )
    return list(session.exec(statement).all())


def list_group_games(session: Session, group_id: int):
    """Return all game rows owned by group members."""
    statement = (
        select(
            Group.groupId.label("groupId"),
            Group.groupName.label("groupName"),
            User.userId.label("userId"),
            User.userName.label("userName"),
            Game.gameId.label("gameId"),
            Game.gameName.label("gameName"),
            UserGame.isAvailable.label("isAvailable"),
        )
        .select_from(Group)
        .join(GroupMember, GroupMember.groupId == Group.groupId)
        .join(User, User.userId == GroupMember.userId)
        .join(UserGame, UserGame.userId == User.userId)
        .join(Game, Game.gameId == UserGame.gameId)
        .where(Group.groupId == group_id)
        .order_by(User.userName, Game.gameName)
    )
    return session.exec(statement).all()


def _build_user_game_read(user_game: UserGame, game_name: str) -> UserGameRead:
    """Convert a database association row into an API schema."""
    return UserGameRead(
        userGameId=user_game.userGameId,
        userId=user_game.userId,
        gameId=user_game.gameId,
        gameName=game_name,
        isAvailable=user_game.isAvailable,
    )
