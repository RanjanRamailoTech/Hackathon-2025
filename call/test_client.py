import asyncio
import websockets
import json

async def send_video_chunks():
    uri = "ws://localhost:8000/ws/interviews/1/"
    
    async with websockets.connect(uri) as websocket:
        # Send video chunks
        with open("/home/suraj-sharma/Downloads/sample_video3.mp4", "rb") as f:
            # while chunk := f.read(10 * 1024 * 1024):  # Read in chunks of 1MB
            await websocket.send(f.read())
            response = await websocket.recv()
            print("Server response:", response)

        # Periodically send heartbeat messages
        while True:
            await asyncio.sleep(10)  # Send every 10 seconds
            await websocket.send(json.dumps({"type": "heartbeat"}))
            print("Sent heartbeat")

asyncio.run(send_video_chunks())
