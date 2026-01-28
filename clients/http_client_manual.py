from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

MCP_URL = "http://127.0.0.1:8000/mcp/"
# Align with latest MCP spec (Nov 25, 2025)
PROTOCOL_VERSION = "2025-11-25"


@dataclass
class McpSession:
    """
    Tracks state for manual MCP JSON-RPC calls.

    Parameters
    ----------
    session_id:
        Server-provided session identifier (header `Mcp-Session-Id`).
    next_id:
        Incrementing JSON-RPC id to correlate requests and responses.
    """

    session_id: Optional[str] = None
    next_id: int = 1


def headers(session: McpSession) -> Dict[str, str]:
    """
    Build HTTP headers for MCP streamable HTTP calls.

    Parameters
    ----------
    session:
        Current session tracker (adds `Mcp-Session-Id` when present).

    Returns
    -------
    Dict[str, str]
        Minimal headers required for JSON + SSE support.
    """
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session.session_id:
        # print(session)
        h["Mcp-Session-Id"] = session.session_id
    return h


def rpc(session: McpSession, method: str, params: Optional[Dict[str, Any]] = None, include_id: bool = True):
    """
    Compose a JSON-RPC 2.0 payload.

    Parameters
    ----------
    session:
        Session tracker supplying incrementing ids.
    method:
        MCP method name (e.g., `initialize`, `tools/list`).
    params:
        Optional method parameters dictionary.
    include_id:
        When False, builds a notification (no id).

    Returns
    -------
    Dict[str, Any]
        JSON-serializable payload ready for POST.
    """
    payload: Dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        payload["params"] = params
    if include_id:
        payload["id"] = session.next_id
        session.next_id += 1
    return payload


def main() -> int:
    """
    Run a minimal MCP HTTP client flow:

    1) initialise the server(captures session id)
    2) send start up notification
    3) list tools
    4) call the `echo` tool

    Returns
    -------
    int
        Zero on success; raises httpx exceptions on HTTP errors.
    """
    s = McpSession()

    with httpx.Client(timeout=30.0) as client:
        init = rpc(
            s,
            "initialize",
            params={
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "httpx-manual", "version": "1.0"},
            },
        )
        r = client.post(MCP_URL, headers=headers(s), json=init)
        r.raise_for_status()
        s.session_id = r.headers.get("Mcp-Session-Id")

        print("Initialise response:")
        print(json.dumps(r.json(), indent=2))
        print(f"Mcp-Session-Id: {s.session_id}")

        notif = rpc(s, "notifications/initialized", params={}, include_id=False)
        r2 = client.post(MCP_URL, headers=headers(s), json=notif)
        if r2.status_code not in (200, 202):
            r2.raise_for_status()

        r3 = client.post(MCP_URL, headers=headers(s), json=rpc(s, "tools/list", params={}))
        r3.raise_for_status()
        print("\nTools/list response:")
        print(json.dumps(r3.json(), indent=2))

        r4 = client.post(
            MCP_URL,
            headers=headers(s),
            json=rpc(s, "tools/call", params={"name": "echo", "arguments": {"text": "Hello from Python client"}}),
        )
        r4.raise_for_status()
        print("\nTools/call (echo) response:")
        print(json.dumps(r4.json(), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
