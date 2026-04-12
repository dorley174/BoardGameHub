"""
Locust load tests for BoardGameHub.

Quality Plan (performance): keep **P95 latency below 200 ms** for critical
read paths under your target load. Locust prints response-time percentiles in
the summary; use the headless run below and review the **95%** column, or export
CSV and gate CI if you automate checks.
"""

from __future__ import annotations

import os
import uuid

from locust import HttpUser, between, task


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class BoardGameHubBrowseUser(HttpUser):
    """
    Simulates a lightweight client: health check, library read, username lookup.

    Note: the coursework text may mention POST for username search; this API
    exposes lookup as **GET /users/search** with a ``username`` query parameter.
    """

    wait_time = between(0.5, 2.0)

    def on_start(self) -> None:
        # Prefer a stable synthetic user so list/search stay valid across requests.
        suffix = uuid.uuid4().hex[:10]
        self.username = os.environ.get("LOCUST_USERNAME", f"locust_user_{suffix}")
        self.user_id = _env_int("LOCUST_USER_ID", 1)

        created = self._ensure_user(self.username)
        if created is not None:
            self.user_id = created

    def _ensure_user(self, username: str) -> int | None:
        with self.client.post(
            "/users",
            json={"userName": username},
            name="POST /users (seed)",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 201):
                payload = response.json()
                return int(payload["userId"])
            if response.status_code == 409:
                response.success()
                return self._user_id_from_search(username)
            response.failure(
                f"seed user failed: {response.status_code} {response.text}"
            )
            return None

    def _user_id_from_search(self, username: str) -> int | None:
        with self.client.get(
            "/users/search",
            params={"username": username},
            name="GET /users/search (resolve id)",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"resolve user id failed: {response.status_code} {response.text}"
                )
                return None
            payload = response.json()
            return int(payload["userId"])

    @task(3)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")

    @task(2)
    def list_user_games(self) -> None:
        self.client.get(
            f"/users/{self.user_id}/games",
            name="GET /users/[id]/games",
        )

    @task(2)
    def search_user_by_username(self) -> None:
        self.client.get(
            "/users/search",
            params={"username": self.username},
            name="GET /users/search",
        )
