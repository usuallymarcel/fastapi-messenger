from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.responses import FileResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.utils.session_token import is_session_valid

from app.dependencies import get_db
from pathlib import Path
import os
from app.config import settings
from app.routes import ws, users, friends, groups

app = FastAPI()

app.include_router(users.router)
app.include_router(ws.router)
app.include_router(friends.router)
app.include_router(groups.router)

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
async def chat(request: Request, db: Session = Depends(get_db)):

    session_valid = is_session_valid(db, request)
    
    if session_valid:
        return FileResponse(BASE_DIR / "static" / "chat" / "index.html" )
    
    return RedirectResponse(url="/", status_code=302)
    

@app.get("/config.js")
async def config_js():
    return Response(content=f"""window.ENV = {{API_URL: "{settings.api_url}"}};""", media_type="application/javascript")
