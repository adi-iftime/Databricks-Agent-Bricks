"""Stdin/stdout JSON helpers for Cursor command hooks (stdlib only)."""

from __future__ import annotations

import json
import sys
from typing import Any, Mapping


def read_stdin_json() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def write_stdout_json(obj: Mapping[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
    sys.stdout.flush()


def exit_block_pre_tool(user_message: str, agent_message: str | None = None) -> None:
    write_stdout_json(
        {
            "permission": "deny",
            "user_message": user_message,
            "agent_message": agent_message or user_message,
        }
    )
    raise SystemExit(2)


def exit_allow_pre_tool() -> None:
    write_stdout_json({"permission": "allow"})
    raise SystemExit(0)


def exit_ask_pre_tool(user_message: str, agent_message: str | None = None) -> None:
    write_stdout_json(
        {
            "permission": "ask",
            "user_message": user_message,
            "agent_message": agent_message or user_message,
        }
    )
    raise SystemExit(0)


def exit_post_additional_context(text: str) -> None:
    write_stdout_json({"additional_context": text})
    raise SystemExit(0)


def exit_post_empty() -> None:
    write_stdout_json({})
    raise SystemExit(0)


def exit_subagent_followup(message: str) -> None:
    write_stdout_json({"followup_message": message})
    raise SystemExit(0)


def exit_shell_allow() -> None:
    write_stdout_json({"permission": "allow"})
    raise SystemExit(0)


def exit_shell_deny(user_message: str, agent_message: str | None = None) -> None:
    write_stdout_json(
        {
            "permission": "deny",
            "user_message": user_message,
            "agent_message": agent_message or user_message,
        }
    )
    raise SystemExit(2)


def exit_shell_ask(user_message: str, agent_message: str | None = None) -> None:
    write_stdout_json(
        {
            "permission": "ask",
            "user_message": user_message,
            "agent_message": agent_message or user_message,
        }
    )
    raise SystemExit(0)
