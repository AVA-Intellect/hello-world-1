# Hello World Docker Compose (API + WebSocket)

This repository contains a minimal, cloud-ready **Hello World** stack using Docker Compose to prove that:

- Multiple containers start successfully
- Containers can communicate over Docker networking
- An HTTP API can perform a WebSocket round trip
- Health can be verified via a single JSON endpoint
- Logs are emitted to stdout and visible via Docker

This is intended as a **deployment proof**, not just a local demo.

---

## Architecture

The stack consists of two services.

### ws (WebSocket service)
- Python WebSocket echo server
- Listens on port 8765
- Logs connections, messages, and disconnects

### api (HTTP API)
- Python Flask service
- Listens on port 8080
- On every request:
  - Connects to the WebSocket service
  - Sends a message
  - Receives an echo response
  - Returns the result as JSON

---

## Service Diagram

```
┌──────────┐       WebSocket        ┌──────────┐
│  api     │  ─────────────────▶   │   ws     │
│  :8080   │  ◀─────────────────   │  :8765   │
└──────────┘        Echo            └──────────┘
```

---

## JSON Response

Both `/` and `/health` return the same JSON payload.

Example response:

```json
{
  "ok": true,
  "service": "api",
  "timestamp_utc": "2025-12-16T22:14:31Z",
  "checks": {
    "websocket_roundtrip": {
      "ws_url": "ws://ws:8765",
      "ws_ok": true,
      "ws_echo": "echo: hello 2025-12-16T22:14:31Z",
      "latency_ms": 12,
      "error": null
    }
  }
}
```

If the WebSocket round trip fails, the endpoint returns HTTP 503.

---

## Logs

All logs are written to stdout and captured by Docker.

View logs with:

```bash
docker compose logs -f
```

Example log output:

```text
[api] connecting to ws://ws:8765
[api] ws reply: echo: hello 2025-12-16T22:14:31Z (12ms)
[ws] client connected: ('172.18.0.3', 54321)
[ws] recv: hello 2025-12-16T22:14:31Z
[ws] client disconnected: ('172.18.0.3', 54321)
```

---

## Running the Stack (Remote Images)

This project is configured to pull prebuilt images from **GitHub Container Registry (GHCR)**.

### Prerequisites
- Docker Desktop
- Logged into GHCR if images are private

```bash
docker login ghcr.io
```

### Start services

```bash
docker compose pull
docker compose up
```

### Test endpoints
- API root: http://localhost:8080/
- Health check: http://localhost:8080/health

---

## Docker Compose Configuration

```yaml
services:
  ws:
    image: ghcr.io/ava-intellect/hello-world-ws:latest
    ports:
      - "8765:8765"

  api:
    image: ghcr.io/ava-intellect/hello-world-api:latest
    ports:
      - "8080:8080"
    environment:
      WS_URL: "ws://ws:8765"
      WS_TIMEOUT_SEC: "3"
```

---

## Local Development (Optional)

For local builds, use a compose override file.

Example `docker-compose.override.yml`:

```yaml
services:
  ws:
    build: ./ws

  api:
    build: ./api
```

Run locally:

```bash
docker compose up --build
```

---

## Use Cases

This repository can be used for:

- Cloud deployment validation
- Container networking verification
- Health check examples
- GitHub Container Registry workflows
- Load balancer and ingress smoke tests
- Teaching and documentation

