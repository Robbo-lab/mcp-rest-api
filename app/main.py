from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from .mcp_server import build_mcp_server

mcp = build_mcp_server()
mcp_asgi_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ensure the MCP session manager runs during FastAPI lifespan.

    Parameters
    ----------
    app:
        FastAPI application instance (unused, provided by FastAPI).

    Yields
    ------
    None
        Context manager contract for FastAPI lifespan hook.

    Raises
    ------
    Any exception propagated from MCP session manager startup/shutdown.
    """
    # IMPORTANT: ensures the MCP internal session manager is running
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="FastAPI + MCP Starter", lifespan=lifespan)
app.router.redirect_slashes = True

# Mount MCP at /mcp (client/docs use trailing slash to avoid redirects)
app.mount("/mcp", mcp_asgi_app)


@app.get("/health")
def health():
    """
    Simple liveness check route.

    Returns
    -------
    dict
        JSON payload confirming service and MCP mount.

    Usage example
    -------------
    ```bash
    curl -s http://127.0.0.1:8000/health
    ```
    """
    return {"ok": True, "service": "fastapi+mcp", "mcp": "/mcp"}
