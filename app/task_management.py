import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
import traceback

from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri
from models.agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class TaskInfo:
    id: str
    status: TaskStatus
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = None
    completed_at: datetime = None

# Global task store
tasks = {}

# Create a thread pool for running agent tasks
agent_executor = ThreadPoolExecutor(max_workers=4)

def run_agent_task(
    task_id: str,
    db,
    agent_id: str,
    dataset_id: Optional[str] = None,
    json_object_id: Optional[str] = None,
    properties: Optional[Dict] = None,
    store_result: bool = False
):
    """Background task to run an agent. This is a synchronous function that runs in a thread."""
    try:
        # Get task from global store
        task = tasks.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
            
        # Update status to running
        task.status = TaskStatus.RUNNING
        
        # Load the agent
        agent = Agent.load(db, agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
            
        # Run the agent (db connection is now managed inside agent.run())
        result = agent.run(
            properties=properties,
            dataset_id=dataset_id,
            json_object_id=json_object_id
        )
        
        # Update task status
        task.status = TaskStatus.COMPLETED
        task.result = {
            "store_result": store_result,
            "result": result
        }
        task.completed_at = datetime.now()
        
    except Exception as e:
        logger.error(f"Error in agent task {task_id}: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        
        # Get task again in case it changed
        task = tasks.get(task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
