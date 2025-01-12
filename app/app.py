import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri
from app.routes import agent_routes, object_routes, task_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the database connection details
    uri = load_database_uri()
    db = SqliteDatabase(uri)
    
    # Provide the database instance to the app
    app.state.db = db

    yield

    # Shutdown
    db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust according to your setup
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
base_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory="react-app/build/static"), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Include routers
app.include_router(agent_routes.router)
app.include_router(object_routes.router)
app.include_router(task_routes.router)

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(full_path: str, request: Request):
    # Serve the index.html file for any route that doesn't match an API endpoint
    index_file_path = os.path.join(os.getcwd(), "react-app", "build", "index.html")
    with open(index_file_path, "r") as file:
        return HTMLResponse(file.read())
