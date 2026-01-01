from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from app.config import settings
from app.routes import ws, users

app = FastAPI()

app.include_router(users.router)
app.include_router(ws.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "api.marcel.co.nz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "login" / "index.html")

@app.get("/chat")
async def chat_screen():
    return FileResponse(BASE_DIR / "static" / "chat" / "index.html" )

@app.get("/config.js")
async def config_js():
    return Response(content=f"""window.ENV = {{API_URL: "{settings.api_url}"}};""", media_type="application/javascript")
