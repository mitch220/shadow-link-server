from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

clients = {}
channels = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    await websocket.send_text("USERNAME")
    username = await websocket.receive_text()

    clients[websocket] = username
    channels[websocket] = "general"

    print(f"{username} connected")

    try:
        while True:

            data = await websocket.receive_text()

            # change channel
            if data.startswith("CHANGE_CHANNEL|"):
                channel = data.split("|")[1]
                channels[websocket] = channel
                continue

            if "|" not in data:
                continue

            channel, message = data.split("|", 1)

            formatted = f"{username}|{channel}|{message}"

            # broadcast
            for client, ch in channels.items():
                if ch == channel:
                    await client.send_text(formatted)

    except WebSocketDisconnect:
        print(f"{username} disconnected")
        del clients[websocket]
        del channels[websocket]


@app.get("/")
def home():
    return {"status": "Shadow Link server running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
