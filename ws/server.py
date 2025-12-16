import asyncio
import websockets

async def echo(websocket, path=None):
    peer = websocket.remote_address
    print(f"[ws] client connected: {peer}", flush=True)
    try:
        async for msg in websocket:
            print(f"[ws] recv: {msg}", flush=True)
            await websocket.send(f"echo: {msg}")
    except Exception as e:
        print(f"[ws] error: {e}", flush=True)
    finally:
        print(f"[ws] client disconnected: {peer}", flush=True)

async def main():
    print("[ws] listening on 0.0.0.0:8765", flush=True)
    async with websockets.serve(echo, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
