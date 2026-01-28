from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List
import asyncio
import os
import psutil

from app.bot_engine import BotManager

app = FastAPI(title="Twitch Automation Controller")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Global Bot Manager instance
bot_manager = BotManager()
chat_task = None

class TokenUpload(BaseModel):
    tokens: str

class ActionRequest(BaseModel):
    channel: str
    action: str # "chat", "follow", "view"
    payload: str = "" # Message for chat, or empty

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    status = bot_manager.get_status()
    return templates.TemplateResponse("index.html", {"request": request, "status": status})

@app.post("/upload_tokens")
async def upload_tokens(tokens: str = Form(...)):
    token_list = tokens.split('\n')
    bot_manager.load_tokens(token_list)
    return {"message": f"Loaded {len(token_list)} tokens"}

@app.post("/start_action")
async def start_action(action_req: ActionRequest, background_tasks: BackgroundTasks):
    global chat_task

    if action_req.action == "follow":
        # Simulate ID lookup or assume channel is ID for this demo
        target_id = action_req.channel
        background_tasks.add_task(bot_manager.follow_target, target_id)
        return {"message": "Follow process started"}

    elif action_req.action == "chat":
        if chat_task and not chat_task.done():
            return JSONResponse(status_code=400, content={"message": "Chat already running"})

        msgs = action_req.payload.split('\n')
        # Create a background task for the infinite chat loop
        chat_task = asyncio.create_task(bot_manager.start_chat_task(action_req.channel, msgs))
        return {"message": "Chat started"}

    elif action_req.action == "view":
        # Placeholder for viewbot logic
        return {"message": "Viewbotting requires browser instances. Starting limited simulation.", "warning": "High resource usage"}

    return {"error": "Invalid action"}

@app.post("/stop_action")
async def stop_action():
    global chat_task
    if chat_task:
        chat_task.cancel()
        try:
            await chat_task
        except asyncio.CancelledError:
            pass
        chat_task = None
        return {"message": "Chat stopped"}
    return {"message": "No active tasks"}

@app.get("/status")
async def get_status():
    status = bot_manager.get_status()
    status["cpu_percent"] = psutil.cpu_percent()
    status["ram_percent"] = psutil.virtual_memory().percent
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
