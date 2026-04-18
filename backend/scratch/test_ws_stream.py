import asyncio
import websockets
import json

async def test_ws_notifications():
    uri = "ws://localhost:8000/ws/notifications"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            if data['type'] == 'ticker_update':
                print(f"[PRICE] {data['data']['symbol']}: Bid={data['data']['bid']} Ask={data['data']['ask']}")
            else:
                print(f"[EVENT] {data}")

if __name__ == "__main__":
    try:
        asyncio.run(test_ws_notifications())
    except KeyboardInterrupt:
        pass
