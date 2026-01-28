# app/mcp_server.py
from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def build_mcp_server() -> FastMCP:
    """
    Create the MCP server and register tools/resources/prompts.
    This object owns the session_manager used by streamable HTTP.

    Returns
    -------
    FastMCP
        Configured server with two demo tools.

    Usage example
    -------------
    ```python
    from app.mcp_server import build_mcp_server
    mcp = build_mcp_server()
    app = mcp.streamable_http_app()
    ```
    """
    mcp = FastMCP(
        "FastAPI MCP Course Server",
        # stateless_http is often easier to understand in the beginning
        stateless_http=True,
        # expose HTTP endpoint at "/" within the mounted app (added an alias in app/main.py for no-trailing-slash)
        streamable_http_path="/",
    )

    # --- Tools -------------------------------------------------
    @mcp.tool()
    def echo(text: str) -> str:
        """Echo the provided text unchanged."""
        return text

    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Return the integer sum of `a` and `b`."""
        return a + b
    print(mcp)
    return mcp
