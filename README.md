# FastAPI + MCP (Streamable HTTP) Starter

This repo is a **teaching starter** for Model Context Protocol (MCP) using **FastAPI** and the **Streamable HTTP** transport (HTTP POST/GET with optional SSE).

It is designed to support the 20‑week plan where students:

- learn REST/HTTP fundamentals,
- learn MCP primitives (tools/resources/prompts),
- compare **stdio vs Streamable HTTP (HTTP/SSE)**,
- and test servers using **curl and Python** (no Postman required).

---

## 1) Prerequisites

- Python 3.10+ (3.11 recommended)

---

## 2) Setup

```bash
cd mcp-fastapi-starter
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
```

---

## 3) Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

You should now have:

- REST health endpoint: `http://127.0.0.1:8000/health`
- MCP endpoint: `http://127.0.0.1:8000/mcp/` (note the trailing slash)

---

## 4) Quick REST check (Week 1 alignment)

```bash
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

Or with plain curl output:

```bash
curl -i http://127.0.0.1:8000/health
```

---

## 5) MCP over Streamable HTTP using curl (manual JSON-RPC)

### 5.1 Initialise (start a session)

**Important:** For Streamable HTTP, clients must send `Accept: application/json, text/event-stream`.
The server may return a `Mcp-Session-Id` response header. If it does, include it on later requests.

```bash
curl -i \
  -X POST http://127.0.0.1:8000/mcp/ \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"initialize",
    "params":{
      "protocolVersion":"2025-11-25",
      "capabilities":{},
      "clientInfo":{"name":"curl","version":"1.0"}
    }
  }'
```

Copy the `Mcp-Session-Id` header value if returned.

### 5.2 Mark the client as initialized

```bash
curl -i \
  -X POST http://127.0.0.1:8000/mcp/ \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Mcp-Session-Id: <PASTE_SESSION_ID>" \
  -d '{
    "jsonrpc":"2.0",
    "method":"notifications/initialized",
    "params":{}
  }'
```

### 5.3 List tools

```bash
curl -s \
  -X POST http://127.0.0.1:8000/mcp/ \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Mcp-Session-Id: <PASTE_SESSION_ID>" \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"tools/list",
    "params":{}
  }' | python -m json.tool
```

### 5.4 Call a tool (`add`)

```bash
curl -s \
  -X POST http://127.0.0.1:8000/mcp/ \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Mcp-Session-Id: <PASTE_SESSION_ID>" \
  -d '{
    "jsonrpc":"2.0",
    "id":3,
    "method":"tools/call",
    "params":{
      "name":"add",
      "arguments":{"a":2,"b":3}
    }
  }' | python -m json.tool
```

### 5.5 Read a resource (`status://summary`)

```bash
curl -s \
  -X POST http://127.0.0.1:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "Mcp-Session-Id: <PASTE_SESSION_ID>" \
  -d '{
    "jsonrpc":"2.0",
    "id":4,
    "method":"resources/read",
    "params":{"uri":"status://summary"}
  }' | python -m json.tool
```

---

## 6) MCP using Python (manual HTTP client)

```bash
python clients/http_client_manual.py
```

It will:

- initialize
- capture `Mcp-Session-Id` if provided
- list tools
- call `echo`

---

## Project layout

```
mcp-fastapi-starter/
  app/
    main.py
    mcp_server.py
  clients/
    http_client_manual.py
  requirements.txt
```

<!-- uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning > /tmp/mcp_uvicorn.log 2>&1 & echo $! -->
