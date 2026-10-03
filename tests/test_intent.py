from __future__ import annotations

from typing import Any

import pytest

from taskmgr import agent
from taskmgr.intent import REFUSAL, Intent, parse_intent


def test_parse_in_scope() -> None:
    assert parse_intent('{"in_scope": true, "reason": "adds a task"}') == Intent(
        True, "adds a task"
    )


def test_parse_out_of_scope_with_surrounding_text() -> None:
    result = parse_intent('Sure:\n{"in_scope": false, "reason": "trivia"}')
    assert result.in_scope is False


@pytest.mark.parametrize("text", ["", "yes", "{bad json}", '{"in_scope": "true"}', "[1]"])
def test_parse_fails_closed(text: str) -> None:
    assert parse_intent(text).in_scope is False


class FakeClient:
    """Records whether the task agent was ever queried."""

    def __init__(self) -> None:
        self.queried = False

    async def query(self, prompt: str) -> None:
        self.queried = True

    async def receive_response(self) -> Any:
        return
        yield


async def test_out_of_scope_takes_no_action(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_classify(message: str, context: str = "") -> Intent:
        return Intent(False, "trivia")

    monkeypatch.setattr(agent, "classify_intent", fake_classify)
    client = FakeClient()
    reply = await agent.guarded_turn(client, "capital of France?")  # type: ignore[arg-type]
    assert reply == REFUSAL
    assert client.queried is False


async def test_in_scope_reaches_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_classify(message: str, context: str = "") -> Intent:
        return Intent(True, "task")

    monkeypatch.setattr(agent, "classify_intent", fake_classify)
    client = FakeClient()
    await agent.guarded_turn(client, "add a task: x")  # type: ignore[arg-type]
    assert client.queried is True
