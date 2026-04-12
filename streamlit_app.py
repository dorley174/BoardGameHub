"""Streamlit demo shell for BoardGameHub (API data is loaded when the backend is up)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import streamlit as st

DEFAULT_API = "http://127.0.0.1:8000"


def _get_json(url: str, timeout: float = 5.0) -> object | None:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return None


st.set_page_config(page_title="BoardGameHub", layout="wide")

st.title("BoardGameHub")
st.markdown(
    "Demo UI for the BoardGameHub API — **individual accounts**, **groups**, "
    "and **meetups** (collections of players and games)."
)

api_base = st.sidebar.text_input("API base URL", DEFAULT_API).rstrip("/")

root_payload = _get_json(f"{api_base}/")
health_payload = _get_json(f"{api_base}/health")
st.sidebar.subheader("API status")
if health_payload is not None:
    st.sidebar.success(f"Health: {health_payload}")
elif root_payload is not None:
    st.sidebar.warning("Health check failed; root endpoint responded.")
else:
    st.sidebar.error("API not reachable at this base URL.")

st.divider()
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Individual accounts")
    st.caption("Planned: user search and profiles (`/users/...`).")
    if root_payload is not None:
        st.json(root_payload)
    else:
        st.info("Stub: run `uvicorn src.main:app` and refresh to preview API metadata.")

with c2:
    st.subheader("Groups")
    st.caption("Planned: groups and members (`/groups/{id}/...`).")
    st.info(
        "Stub: table of groups and member rosters will bind to the groups API "
        "once list endpoints are exposed."
    )

with c3:
    st.subheader("Meetups")
    st.caption("Planned: sessions from libraries and availability.")
    if health_payload is not None:
        st.json({"meetups": "placeholder", "backend": health_payload})
    else:
        st.info(
            "Stub: meetup scheduling views will consume user, group, and game APIs."
        )

st.divider()
st.caption(
    "This page is a front-end placeholder: wire endpoints from `src/api/` "
    "as they stabilize."
)
