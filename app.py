from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
from typing import List, Dict, Any
from database import init_db, get_db
from agents.primary_agent import PrimaryAgent
from models import Task, Event, Note

app = FastAPI(title="Multi-Agent Task Manager")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="/workspaces/Gen-AI-APAC-/templates")

# Initialize database
init_db()

# Global agent instance
primary_agent = PrimaryAgent()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    with open("/workspaces/Gen-AI-APAC-/templates/index.html", "r") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/chat", response_class=HTMLResponse)
async def chat_view(request: Request):
    with open("/workspaces/Gen-AI-APAC-/templates/chat.html", "r") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/database", response_class=HTMLResponse)
async def database_view(request: Request):
    from jinja2 import Template
    db = get_db()
    try:
        tasks = db.query(Task).all()
        events = db.query(Event).all()
        notes = db.query(Note).all()

        with open("/workspaces/Gen-AI-APAC-/templates/database.html", "r") as f:
            template_content = f.read()

        template = Template(template_content)
        html = template.render(
            tasks=tasks,
            events=events,
            notes=notes
        )
        return HTMLResponse(html)
    finally:
        db.close()

@app.get("/architecture", response_class=HTMLResponse)
async def architecture_view(request: Request):
    with open("/workspaces/Gen-AI-APAC-/templates/architecture.html", "r") as f:
        content = f.read()
    return HTMLResponse(content)

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        # Send initial status
        await websocket.send_json({"type": "status", "active_agents": []})
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "status_request":
                # Send current status
                await websocket.send_json({"type": "status", "active_agents": []})
                continue
            
            user_input = message.get("message", "")
            
            # Send agent status
            await websocket.send_json({"type": "status", "active_agents": ["Primary"]})
            
            # Process with primary agent
            response = await primary_agent.process_request(user_input, websocket)
            
            await websocket.send_json({"type": "response", "content": response})
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
    finally:
        await websocket.close()

@app.post("/api/chat")
async def chat_api(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    response = await primary_agent.process_request(user_input)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)