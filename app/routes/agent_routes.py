import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Optional
import traceback

from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse

from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri
from app.task_management import TaskStatus, TaskInfo, tasks, agent_executor, run_agent_task
from models.agent import Agent
from models.json_object import Json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["agents"])

@router.post("/{agent_id}/start_run")
async def start_run_agent(
    agent_id: str,
    request: Request,
    dataset_id: Optional[str] = None,
    json_object_id: Optional[str] = None,
    properties: Optional[Dict] = Body(None),
    store_result: bool = False
) -> JSONResponse:
    """Start an asynchronous agent run task.
    
    Args:
        agent_id: ID of the agent to run
        dataset_id: Optional ID of dataset to extract experiment description and data from
        json_object_id: Optional ID of JSON object to extract properties from
        properties: Optional dictionary of properties (highest priority)
        store_result: Optional boolean indicating whether to store result in DB (default False)
    
    Returns:
        JSONResponse containing the task ID
    """
    try:
        # Create new task immediately
        task_id = str(uuid.uuid4())
        tasks[task_id] = TaskInfo(
            id=task_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            result={"store_result": store_result}  # Store the flag in task info
        )
        
        # Submit task to thread pool
        agent_executor.submit(
            run_agent_task,
            task_id=task_id,
            db=SqliteDatabase(load_database_uri()),  # Create new db connection for thread
            agent_id=agent_id,
            dataset_id=dataset_id,
            json_object_id=json_object_id,
            properties=properties,
            store_result=store_result
        )
        
        # Return task ID immediately as proper JSON
        return JSONResponse(content={"task_id": task_id})
        
    except Exception as e:
        logger.error(f"Error starting agent task: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent_task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of an agent run task.
    
    Args:
        task_id: ID of the task to check
        
    Returns:
        JSONResponse containing task status and result if complete.
        If task.result["store_result"] is True, creates a new JSON object in database
        and returns its ID. Otherwise returns the result directly.
    """
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    response = {
        "task_id": task.id,
        "status": task.status.value,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None
    }
    
    if task.status == TaskStatus.COMPLETED:
        if task.result.get("store_result", False):
            # Create new JSON object in database
            db = SqliteDatabase(load_database_uri())
            json_obj = Json(db)
            json_obj.create(task.result["result"])  # The actual result is nested
            response["result"] = {"json_id": json_obj.object_id}
        else:
            # Return result directly
            response["result"] = task.result["result"]
    elif task.status == TaskStatus.FAILED:
        response["error"] = task.error
        
    # Return as proper JSON response with explicit headers
    return JSONResponse(
        content=response,
        headers={"Content-Type": "application/json"}
    )

@router.post("/{agent_id}/run")
async def run_agent(
    agent_id: str,
    request: Request,
    dataset_id: Optional[str] = None,
    json_object_id: Optional[str] = None,
    properties: Optional[Dict] = Body(None)
) -> Dict:
    """Run an agent synchronously (legacy endpoint).
    
    This endpoint is maintained for backward compatibility but using
    start_run_agent + get_task_status is recommended for better reliability.
    
    Args:
        agent_id: ID of the agent to run
        dataset_id: Optional ID of dataset to extract experiment description and data from
        json_object_id: Optional ID of JSON object to extract properties from
        properties: Optional dictionary of properties (highest priority)
    
    Returns:
        JSON response containing the agent's output
    """
    start_time = time.time()
    db = request.app.state.db
    
    try:
        # Log input parameters
        logger.info(f"Running agent {agent_id} with parameters:")
        logger.info(f"dataset_id: {dataset_id}")
        logger.info(f"json_object_id: {json_object_id}")
        logger.info(f"properties: {properties}")
        
        # Load the agent
        agent = Agent.load(db, agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        logger.info(f"Agent loaded: {agent.name}")
        logger.info(f"Prompt template: {agent.prompt_template}")
            
        # Run the agent (db connection is now managed inside agent.run())
        result = agent.run(
            properties=properties,
            dataset_id=dataset_id,
            json_object_id=json_object_id
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Agent run completed successfully in {elapsed_time:.2f} seconds")
        return result
        
    except ValueError as e:
        # Handle specific ValueError exceptions (e.g. format string errors)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.error(f"ValueError in run_agent after {elapsed_time:.2f} seconds: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle any other unexpected errors
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.error(f"Unexpected error in run_agent after {elapsed_time:.2f} seconds: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error running agent: {str(e)}")
