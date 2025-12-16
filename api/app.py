import os
import time
import asyncio
from datetime import datetime, timezone

from flask import Flask, jsonify, make_response
import websockets

app = Flask(__name__)

WS_URL = os.getenv("WS_URL", "ws://ws:8765")
WS_TIMEOUT_SEC = float(os.getenv("WS_TIMEOUT_SEC", "3"))

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

async def ws_roundtrip():
    msg = f"hello {utc_now_iso()}"
    started = time.time()

    print(f"[api] connecting to {WS_URL}", flush=True)
    try:
        async with websockets.connect(
            WS_URL,
            open_timeout=WS_TIMEOUT_SEC,
            close_timeout=WS_TIMEOUT_SEC,
        ) as ws:
            await asyncio.wait_for(ws.send(msg), timeout=WS_TIMEOUT_SEC)
            echo = await asyncio.wait_for(ws.recv(), timeout=WS_TIMEOUT_SEC)

        latency_ms = int((time.time() - started) * 1000)
        print(f"[api] ws reply: {echo} ({latency_ms}ms)", flush=True)
        return True, echo, latency_ms, None

    except Exception as e:
        latency_ms = int((time.time() - started) * 1000)
        print(f"[api] ws check failed after {latency_ms}ms: {e}", flush=True)
        return False, None, latency_ms, str(e)

def json_response(payload: dict, status_code: int = 200):
    resp = make_response(jsonify(payload), status_code)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    resp.headers["Cache-Control"] = "no-store"
    return resp

def run_checks():
    ok, echo, latency_ms, err = asyncio.run(ws_roundtrip())
    payload = {
        "ok": True,  # the API endpoint itself is reachable
        "service": "api",
        "timestamp_utc": utc_now_iso(),
        "checks": {
            "websocket_roundtrip": {
                "ws_url": WS_URL,
                "ws_ok": ok,
                "ws_echo": echo,
                "latency_ms": latency_ms,
                "error": err,
            }
        },
    }
    # If WS fails, return 503 so cloud health checks can catch it
    return payload, (200 if ok else 503)

@app.route("/")
def root():
    payload, code = run_checks()
    return json_response(payload, code)

@app.route("/health")
def health():
    payload, code = run_checks()
    return json_response(payload, code)

if __name__ == "__main__":
    print(f"[api] starting, WS_URL={WS_URL}, timeout={WS_TIMEOUT_SEC}s", flush=True)
    app.run(host="0.0.0.0", port=8080)
