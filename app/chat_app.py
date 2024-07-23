from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json

app = FastAPI()

# In-memory storage for conversation history and current hypothesis
conversation_history: List[Dict[str, Any]] = []
current_hypothesis: Dict[str, Any] = {}
run_pause_state = False
query_limit = 100
current_query_count = 0

class Dataset:
    def __init__(self, data: str, description: str):
        self.data = data  # CSV format data
        self.description = description

class LLM:
    def __init__(self, parameters: Dict[str, Any]):
        self.parameters = parameters

    def query(self, prompt: str) -> str:
        # Simulate querying an LLM with given parameters
        return f"Response to '{prompt}' with parameters {self.parameters}"

# Example dataset and LLMs
dataset = Dataset("gene,expression\nG1,2.5\nG2,3.6", "Description of the dataset")
llm_agent1 = LLM({"name": "Agent 1", "param": "value1"})
llm_agent2 = LLM({"name": "Agent 2", "param": "value2"})

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