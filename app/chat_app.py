from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
import json
import os
from contextlib import asynccontextmanager
from app.sqlite_database import SqliteDatabase, load_database_config
from app.cxdb import CXDB
from models.llm import LLM
from models.analyst import Analyst  
from models.chat import Chat

app = FastAPI()

# Setup templates and static files
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the database connection details
    _, uri, _, _ = load_database_config()
    db = SqliteDatabase(uri)
    
    # Provide the database instance to the app
    app.state.db = db

    # Add the CXDB instance to the app for dialog and context management
    app.state.cxdb = CXDB()

    yield

    # Shutdown
    db.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path) as f:
        return HTMLResponse(content=f.read())

# In-memory storage for conversation history and current hypothesis
conversation_history: List[Dict[str, Any]] = []
current_hypothesis: Dict[str, Any] = {}
run_pause_state = False
query_limit = 100
current_query_count = 0

# load two Analysts
analyst_1 = Analyst.load("agent1_id")
analyst_2 = Analyst.load("agent2_id")

# load their respective LLMs
llm_1 = LLM.load(analyst_1.llm_id)
llm_2 = LLM.load(analyst_2.llm_id)

# Create a Chat
discussion = Chat("Discussion", 
                  analyst_1, analyst_2,
                  llm_1, llm_2,
                  query_limit=query_limit)


async def handle_agent(agent, websocket: WebSocket):
    global current_hypothesis, current_query_count, run_pause_state
    while current_query_count < query_limit and not run_pause_state:
        if current_hypothesis:
            prompt = f"Critique: {current_hypothesis['content']}"
        else:
            prompt = f"Propose a hypothesis about the dataset: {dataset.description}"

        response = agent.query(prompt)
        current_hypothesis = {"agent": agent.parameters["name"], "content": response}
        conversation_history.append(current_hypothesis)
        current_query_count += 1

        # Send the updated conversation and hypothesis
        await websocket.send_text(json.dumps({
            "conversation": conversation_history,
            "current_hypothesis": current_hypothesis,
            "query_count": current_query_count
        }))

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await websocket.accept()
    agent = llm_agent1 if agent_id == "agent1" else llm_agent2
    try:
        await handle_agent(agent, websocket)
    except WebSocketDisconnect:
        print(f"Agent {agent_id} disconnected")

@app.get("/toggle_run_pause")
async def toggle_run_pause():
    global run_pause_state
    run_pause_state = not run_pause_state
    return {"run_pause_state": run_pause_state}

@app.get("/reset_query_count")
async def reset_query_count():
    global current_query_count
    current_query_count = 0
    return {"current_query_count": current_query_count}