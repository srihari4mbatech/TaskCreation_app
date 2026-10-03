"""Claude Agent SDK wiring."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    ToolUseBlock,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SYSTEM_PROMPT = """You are a task management assistant.
Tasks live in data/tasks.json: a JSON list of objects with fields
id (int), title (str), status ("todo" | "in_progress" | "done"),
priority ("low" | "medium" | "high"), due (YYYY-MM-DD or null),
notes (str) and parent_id (int or null, for subtasks).
Read the file before changing it, keep it valid JSON, give new tasks the next unused id,
and never drop fields. Use the available skills for prioritising, planning and
breaking down work. Reply briefly and say what you changed."""


def build_options() -> ClaudeAgentOptions:
    """Build agent options with project skills enabled.

    Returns:
        Options that load ``.claude/skills`` and allow file tools on the task file.
    """
    return ClaudeAgentOptions(
        cwd=str(PROJECT_ROOT),
        setting_sources=["project"],
        allowed_tools=["Skill", "Read", "Write", "Edit"],
        permission_mode="acceptEdits",
        system_prompt=SYSTEM_PROMPT,
    )


async def run_turn(client: ClaudeSDKClient, prompt: str) -> AsyncIterator[str]:
    """Send a prompt and stream the agent's text replies.

    Args:
        client: A connected SDK client (keeps conversation context across turns).
        prompt: The user's message.

    Yields:
        Text chunks, plus a short note whenever a skill is invoked.
    """
    await client.query(prompt)
    async for message in client.receive_response():
        if not isinstance(message, AssistantMessage):
            continue
        for block in message.content:
            if isinstance(block, TextBlock):
                yield block.text
            elif isinstance(block, ToolUseBlock) and block.name == "Skill":
                skill = block.input.get("skill") or block.input.get("command", "skill")
                logger.info("Skill invoked: %s", skill)
                yield f"_Using skill: {skill}_"
