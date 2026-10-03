"""Streamlit UI: task board plus a chat panel backed by the Claude Agent SDK."""

from __future__ import annotations

import asyncio
import logging
import os
import threading
from typing import Any

import streamlit as st
from claude_agent_sdk import ClaudeSDKClient

from taskmgr.agent import build_options, run_turn
from taskmgr.models import Status
from taskmgr.store import TaskStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATUS_LABELS = {Status.TODO: "To do", Status.IN_PROGRESS: "In progress", Status.DONE: "Done"}
PRIORITY_ICONS = {"high": "🔴", "medium": "🟡", "low": "🟢"}


@st.cache_resource
def get_loop() -> asyncio.AbstractEventLoop:
    """Start one background event loop that owns the SDK client."""
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()
    return loop


@st.cache_resource
def get_client() -> ClaudeSDKClient:
    """Create and connect the agent client once per server process."""
    client = ClaudeSDKClient(options=build_options())
    asyncio.run_coroutine_threadsafe(client.connect(), get_loop()).result(timeout=60)
    return client


def ask_agent(prompt: str) -> str:
    """Run one agent turn and return the combined reply text."""

    # Resolve the client here: calling it inside the coroutine would block the
    # background loop on its own connect() call and deadlock.
    client = get_client()

    async def collect() -> str:
        return "\n\n".join([chunk async for chunk in run_turn(client, prompt)])

    return asyncio.run_coroutine_threadsafe(collect(), get_loop()).result()


def render_board(store: TaskStore) -> None:
    """Show tasks grouped by status."""
    tasks = store.list_tasks()
    columns = st.columns(len(STATUS_LABELS))
    for column, (status, label) in zip(columns, STATUS_LABELS.items(), strict=True):
        with column:
            group = [t for t in tasks if t.status == status]
            st.subheader(f"{label} ({len(group)})")
            for task in group:
                icon = PRIORITY_ICONS.get(task.priority.value, "")
                prefix = "↳ " if task.parent_id else ""
                with st.container(border=True):
                    st.markdown(f"{prefix}{icon} **#{task.id} {task.title}**")
                    if task.due:
                        st.caption(f"Due {task.due.isoformat()}")
                    if task.notes:
                        st.caption(task.notes)


def main() -> None:
    """Render the app."""
    st.set_page_config(page_title="Task Manager", page_icon="✅", layout="wide")
    st.title("✅ Agentic Task Manager")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.warning("ANTHROPIC_API_KEY is not set; the agent may fail unless you are logged in.")

    store = TaskStore()
    render_board(store)

    st.divider()
    st.subheader("Chat with your task agent")
    st.caption(
        'Try: "add a task: write report, high priority" · "break down: launch website"'
        ' · "plan my day"'
    )

    history: list[dict[str, Any]] = st.session_state.setdefault("history", [])
    for entry in history:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])

    if prompt := st.chat_input("Ask the agent to manage your tasks"):
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"), st.spinner("Working..."):
            try:
                reply = ask_agent(prompt)
            except Exception:
                logger.exception("Agent turn failed")
                reply = "Sorry, the agent failed. Check the server logs and your API key."
            st.markdown(reply)
        history.append({"role": "assistant", "content": reply})
        st.rerun()


main()
