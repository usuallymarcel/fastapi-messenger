from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from app.config import settings
from app.routes import users

app = FastAPI()

app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "api.marcel.co.nz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)


# manager = ConnectionManager()
# messages = []

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/login")
async def login_screen():
    return FileResponse(BASE_DIR / "static" / "login" / "index.html" )

@app.get("/config.js")
async def config_js():
    return Response(content=f"""window.ENV = {{API_URL: "{settings.api_url}"}};""", media_type="application/javascript")


# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
#     # client_join_msg = f"Client #{client_id} joined the chat"
#     # client_leave_msg = f"Client #{client_id} left the chat"

#     await manager.connect(websocket)
#     for msg in messages:
#         await manager.send_personal_message(msg, websocket)
#     # await manager.broadcast(client_join_msg)
#     # messages.append(client_join_msg)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             client_says_msg = f"Client #{client_id} says: {data}"
#             await manager.broadcast(client_says_msg)
#             messages.append(client_says_msg)
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         # await manager.broadcast(client_leave_msg)
#         # messages.append(client_leave_msg)