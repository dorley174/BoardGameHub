from __future__ import annotations

from uuid import uuid4

from locust import HttpUser, between, task


class BoardGameHubUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:
        suffix = uuid4().hex[:8]

        self.owner_username = f"locust_owner_{suffix}"
        self.friend_username = f"locust_friend_{suffix}"
        self.group_name = f"locust_group_{suffix}"
        self.game_name = f"Catan-{suffix}"
        self.is_available = True

        self.user_id = self._create_user(self.owner_username)
        self.friend_user_id = self._create_user(self.friend_username)

        self.group_id = self._create_group(self.group_name, self.user_id)
        self._invite_member(self.group_id, self.friend_username, self.user_id)

        self.user_game_id = self._add_game(
            self.user_id,
            self.game_name,
            self.is_available,
        )

    def _create_user(self, username: str) -> int:
        with self.client.post(
            "/users",
            json={"userName": username},
            name="/users [POST]",
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(
                    f"create user failed: {response.status_code} {response.text}"
                )
                raise RuntimeError("cannot create user")

            payload = response.json()
            return payload["userId"]

    def _create_group(self, name: str, creator_user_id: int) -> int:
        with self.client.post(
            "/groups",
            json={"groupName": name, "creatorUserId": creator_user_id},
            name="/groups [POST]",
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(
                    f"create group failed: {response.status_code} {response.text}"
                )
                raise RuntimeError("cannot create group")

            payload = response.json()
            return payload["groupId"]

    def _invite_member(
        self,
        group_id: int,
        username: str,
        invited_by_user_id: int,
    ) -> None:
        with self.client.post(
            f"/groups/{group_id}/members",
            json={
                "username": username,
                "invitedByUserId": invited_by_user_id,
            },
            name="/groups/[id]/members [POST]",
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(
                    f"invite member failed: {response.status_code} {response.text}"
                )

    def _add_game(self, user_id: int, game_name: str, is_available: bool) -> int:
        with self.client.post(
            f"/users/{user_id}/games",
            json={"gameName": game_name, "isAvailable": is_available},
            name="/users/[id]/games [POST]",
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(
                    f"add game failed: {response.status_code} {response.text}"
                )
                raise RuntimeError("cannot add game")

            payload = response.json()
            return payload["userGameId"]

    @task(2)
    def root(self) -> None:
        self.client.get("/", name="/ [GET]")

    @task(3)
    def health(self) -> None:
        self.client.get("/health", name="/health [GET]")

    @task(2)
    def get_user(self) -> None:
        self.client.get(f"/users/{self.user_id}", name="/users/[id] [GET]")

    @task(2)
    def get_user_by_username(self) -> None:
        self.client.get(
            "/users/search",
            params={"username": self.owner_username},
            name="/users/search [GET]",
        )

    @task(4)
    def list_user_games(self) -> None:
        self.client.get(
            f"/users/{self.user_id}/games",
            name="/users/[id]/games [GET]",
        )

    @task(2)
    def update_game_status(self) -> None:
        self.is_available = not self.is_available
        self.client.patch(
            f"/users/{self.user_id}/games/{self.user_game_id}/status",
            json={"isAvailable": self.is_available},
            name="/users/[id]/games/[user_game_id]/status [PATCH]",
        )

    @task(1)
    def list_group_members(self) -> None:
        self.client.get(
            f"/groups/{self.group_id}/members",
            name="/groups/[id]/members [GET]",
        )

    @task(1)
    def list_group_games(self) -> None:
        self.client.get(
            f"/groups/{self.group_id}/games",
            name="/groups/[id]/games [GET]",
        )

    @task(1)
    def replace_game(self) -> None:
        delete_response = self.client.delete(
            f"/users/{self.user_id}/games/{self.user_game_id}",
            name="/users/[id]/games/[user_game_id] [DELETE]",
        )

        if delete_response.status_code in (200, 204):
            suffix = uuid4().hex[:6]
            self.game_name = f"Catan-{suffix}"
            self.user_game_id = self._add_game(
                self.user_id,
                self.game_name,
                self.is_available,
            )