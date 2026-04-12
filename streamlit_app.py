"""Streamlit UI for BoardGameHub — talks to the FastAPI backend."""

from __future__ import annotations

import json
from typing import Any

import httpx
import streamlit as st

DEFAULT_API = "http://127.0.0.1:8000"


def _detail_from_response(resp: httpx.Response) -> str:
    """Extract error details from the API response."""
    try:
        data = resp.json()
    except (json.JSONDecodeError, ValueError):
        return resp.text.strip() or f"HTTP {resp.status_code}"
    
    detail = data.get("detail")
    if detail is None:
        return f"HTTP {resp.status_code}"
    
    if isinstance(detail, list):
        parts = []
        for item in detail:
            if isinstance(item, dict):
                loc = item.get("loc", [])
                msg = item.get("msg", "")
                parts.append(f"{loc}: {msg}" if loc else str(msg))
            else:
                parts.append(str(item))
        return "; ".join(parts) if parts else str(data)
    
    return str(detail)


def _api_request(
    method: str,
    base: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: float = 10.0,
) -> tuple[bool, Any | None, str | None]:
    """Perform an HTTP request. Returns (ok, data_or_none, error_message_or_none)."""
    base = base.rstrip("/")
    url = f"{base}{path}"
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.request(method, url, json=json_body, params=params)
    except (httpx.RequestError, OSError) as exc:
        return False, None, f"Network / Connection error: {exc}"

    if resp.status_code == 204:
        return True, None, None

    try:
        payload = resp.json() if resp.content else None
    except (json.JSONDecodeError, ValueError):
        payload = None

    if 200 <= resp.status_code < 300:
        return True, payload, None

    err = _detail_from_response(resp)
    return False, payload, err


def _health_check(base: str) -> tuple[bool, Any | None]:
    """Check if the backend API is healthy."""
    ok, data, _ = _api_request("GET", base, "/health")
    return ok, data


st.set_page_config(page_title="BoardGameHub", layout="wide")

st.title("BoardGameHub")
st.markdown(
    "API Interface: **users**, **game library**, and **groups**."
)

if "current_user" not in st.session_state:
    st.session_state.current_user = None  # {"userId", "userName"} | None
if "last_group_id" not in st.session_state:
    st.session_state.last_group_id = None

api_base = st.sidebar.text_input("API base URL", DEFAULT_API).rstrip("/")

st.sidebar.subheader("API Status")
health_ok, health_payload = _health_check(api_base)
if health_ok and health_payload is not None:
    st.sidebar.success(f"API Connection: {health_payload}")
else:
    st.sidebar.error(
        "Backend is unavailable at this address. Run `uvicorn src.main:app` "
        "and refresh the page."
    )

st.sidebar.divider()
st.sidebar.subheader("Quality Plan")
st.sidebar.info(
    "**Status:** The interface operates in conjunction with a project"
)

if st.session_state.current_user:
    st.sidebar.caption("Current User (for games and groups)")
    st.sidebar.write(
        f"**{st.session_state.current_user['userName']}** "
        f"(id: `{st.session_state.current_user['userId']}`)"
    )
    if st.sidebar.button("Reset current user"):
        st.session_state.current_user = None
        st.rerun()

tab_users, tab_games, tab_groups = st.tabs(
    ["Users", "Games", "Groups"]
)

with tab_users:
    st.subheader("Users")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Create User**")
        new_username = st.text_input("Username", key="create_u")
        if st.button("Create", key="btn_create_u"):
            if not new_username or not new_username.strip():
                st.warning("Please enter a username.")
            else:
                ok, data, err = _api_request(
                    "POST",
                    api_base,
                    "/users",
                    json_body={"userName": new_username.strip()},
                )
                if ok and isinstance(data, dict):
                    st.success("User created.")
                    st.session_state.current_user = {
                        "userId": data["userId"],
                        "userName": data["userName"],
                    }
                    st.json(data)
                else:
                    st.error(err or "Failed to create user.")

    with col_b:
        st.markdown("**Find by Username**")
        search_username = st.text_input("Username to search", key="search_u")
        if st.button("Find", key="btn_search_u"):
            if not search_username or not search_username.strip():
                st.warning("Please enter a username.")
            else:
                ok, data, err = _api_request(
                    "GET",
                    api_base,
                    "/users/search",
                    params={"username": search_username.strip()},
                )
                if ok and isinstance(data, dict):
                    st.success("Profile found.")
                    st.session_state.current_user = {
                        "userId": data["userId"],
                        "userName": data["userName"],
                    }
                    st.markdown("**Basic Information**")
                    st.write(f"- **ID:** `{data.get('userId')}`")
                    st.write(f"- **Username:** `{data.get('userName')}`")
                else:
                    st.error(err or "User not found.")

    if st.session_state.current_user:
        st.caption(
            "The selected user is used in the 'Games' and 'Groups' tabs."
        )

with tab_games:
    st.subheader("Games")
    cu = st.session_state.current_user
    if not cu:
        st.info(
            "First, create or find a user in the 'Users' tab to link a game library."
        )
    else:
        uid = cu["userId"]
        st.caption(f"Library for **{cu['userName']}** (id: `{uid}`)")

        game_name = st.text_input("Game title", key="game_title")
        if st.button("Add to library", key="btn_add_game"):
            if not game_name or not game_name.strip():
                st.warning("Please enter a game title.")
            else:
                ok, data, err = _api_request(
                    "POST",
                    api_base,
                    f"/users/{uid}/games",
                    json_body={
                        "gameName": game_name.strip(),
                        "isAvailable": True,
                    },
                )
                if ok:
                    st.success("Game added.")
                    st.rerun()
                else:
                    st.error(err or "Failed to add game.")

        if st.button("Refresh game list", key="btn_refresh_games"):
            st.rerun()

        ok_list, games, err_list = _api_request(
            "GET",
            api_base,
            f"/users/{uid}/games",
        )
        if not ok_list:
            st.error(err_list or "Failed to load game list.")
        elif not games:
            st.info("No games in the library yet.")
        else:
            st.markdown("**Your Games**")
            for g in games:
                if not isinstance(g, dict):
                    continue
                ugid = g.get("userGameId")
                name = g.get("gameName", "")
                avail = bool(g.get("isAvailable", True))
                c1, c2 = st.columns([3, 1])
                with c1:
                    status_label = "Available" if avail else "Unavailable"
                    st.write(f"**{name}** — `{status_label}` (Entry ID: `{ugid}`)")
                with c2:
                    new_avail = st.toggle(
                        "Available",
                        value=avail,
                        key=f"toggle_{ugid}",
                        help="Toggle off for Unavailable",
                    )
                    if new_avail != avail:
                        ok_p, _, err_p = _api_request(
                            "PATCH",
                            api_base,
                            f"/users/{uid}/games/{ugid}/status",
                            json_body={"isAvailable": new_avail},
                        )
                        if ok_p:
                            st.rerun()
                        else:
                            st.error(err_p or "Failed to update status.")

with tab_groups:
    st.subheader("Groups")
    cu = st.session_state.current_user
    if not cu:
        st.info(
            "Please specify a user in the 'Users' tab "
            "(creating groups and invitations require a user ID)."
        )
    else:
        creator_id = cu["userId"]
        st.caption(f"Acting as **{cu['userName']}** (id: `{creator_id}`)")

        gname = st.text_input("New group name", key="group_name_new")
        if st.button("Create Group", key="btn_create_group"):
            if not gname or not gname.strip():
                st.warning("Please enter a group name.")
            else:
                ok, data, err = _api_request(
                    "POST",
                    api_base,
                    "/groups",
                    json_body={
                        "groupName": gname.strip(),
                        "creatorUserId": creator_id,
                    },
                )
                if ok and isinstance(data, dict):
                    st.success("Group created.")
                    gid_new = data.get("groupId")
                    st.session_state.last_group_id = gid_new
                    if gid_new:
                        st.session_state.collective_group_id = int(gid_new)
                    st.json(data)
                else:
                    st.error(err or "Failed to create group.")

        st.markdown("**Group Invitation**")
        gid_default = int(st.session_state.last_group_id or 0)
        group_id = st.number_input(
            "Group ID",
            min_value=0,
            value=gid_default,
            step=1,
            key="group_id_invite",
        )
        invite_username = st.text_input(
            "Friend's username to invite",
            key="invite_uname",
        )
        if st.button("Invite", key="btn_invite"):
            if group_id <= 0:
                st.warning("Please provide a positive Group ID.")
            elif not invite_username or not invite_username.strip():
                st.warning("Please enter the username of the person to invite.")
            else:
                ok, data, err = _api_request(
                    "POST",
                    api_base,
                    f"/groups/{int(group_id)}/members",
                    json_body={
                        "username": invite_username.strip(),
                        "invitedByUserId": creator_id,
                    },
                )
                if ok:
                    st.success("Member added.")
                    if isinstance(data, dict):
                        st.json(data)
                else:
                    st.error(err or "Failed to invite user.")

        st.markdown("**Collective Group Game List**")
        gid_games = st.number_input(
            "Group ID (for game list)",
            min_value=0,
            value=gid_default,
            step=1,
            key="group_id_games",
        )
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Load Group Games", key="btn_group_games"):
                if int(gid_games) <= 0:
                    st.warning("Please provide a positive Group ID.")
                else:
                    st.session_state.collective_group_id = int(gid_games)
                    st.rerun()
        with b2:
            if st.button("Reset List", key="btn_clear_group_games"):
                st.session_state.pop("collective_group_id", None)
                st.rerun()

        load_id = st.session_state.get("collective_group_id")

        if load_id and load_id > 0:
            ok_m, members, err_m = _api_request(
                "GET",
                api_base,
                f"/groups/{load_id}/members",
            )
            ok_g, group_games, err_g = _api_request(
                "GET",
                api_base,
                f"/groups/{load_id}/games",
            )

            if ok_m and members:
                st.markdown("**Members**")
                for m in members:
                    if isinstance(m, dict):
                        st.write(
                            f"- `{m.get('userName')}` (User ID: `{m.get('userId')}`)"
                        )
            elif not ok_m:
                st.warning(err_m or "Failed to load members.")

            if ok_g and group_games:
                st.markdown("**Games of all Members**")
                for row in group_games:
                    if not isinstance(row, dict):
                        continue
                    u = "Available" if row.get("isAvailable") else "Unavailable"
                    st.write(
                        f"- **{row.get('gameName')}** — {u} "
                        f"({row.get('userName')}, game id `{row.get('gameId')}`)"
                    )
            elif not ok_g:
                st.error(err_g or "Failed to load group game list.")
            elif ok_g and not group_games:
                st.info("Group members have no games in their libraries yet.")

st.divider()
st.caption(
    "When the backend is unavailable, requests are handled with error messages; "
    "the interface does not crash."
)