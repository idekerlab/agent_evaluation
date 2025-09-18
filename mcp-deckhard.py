# /// script
# dependencies = ["fastmcp"]
# ///

"""
FastMCP Deckhard Server
--------------------------------
A simple FastMCP server that provides access to the Deckhard AI research workflow 
management system.
"""

from typing import Dict, Optional
import httpx
import logging
import asyncio
import json
import traceback

from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create server
mcp = FastMCP("Deckhard")

# Configuration
BASE_URL = "http://localhost:3000"

# No longer defining allowed object types - allowing all object types

@mcp.tool(name="test_long_operation", description="Test a long-running operation")
async def test_long_operation(sleep_seconds: int) -> Dict:
    """Test how the system handles a long-running operation by sleeping for the specified duration.
    
    Args:
        sleep_seconds: Number of seconds to sleep
        
    Returns:
        Dictionary containing operation status and duration
    """
    logger.debug(f"test_long_operation called with duration {sleep_seconds} seconds")
    try:
        start_time = asyncio.get_event_loop().time()
        await asyncio.sleep(sleep_seconds)
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        logger.debug(f"test_long_operation completed after {duration:.2f} seconds")
        return {
            "status": "success",
            "duration": duration,
            "requested_sleep": sleep_seconds
        }
    except Exception as e:
        error_msg = f"Error in test_long_operation: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool(name="system_description", description="Get a description of the Deckhard system")
def system_description() -> str:
    """Get a description of the Deckhard AI research workflow management system."""
    logger.debug("system_description tool called")
    return """Deckhard is an AI research workflow management system designed to facilitate 
hypothesis generation and evaluation through LLM-powered agents. It provides structured 
workflows for managing AI research projects, including hypothesis generation, data analysis, 
and result evaluation."""

@mcp.tool(name="get_deckhard_object_specs", description="Get specifications for Deckhard object types")
def get_deckhard_object_specs() -> Dict:
    """Get specifications for all Deckhard object types."""
    logger.debug("get_deckhard_object_specs tool called")
    with httpx.Client() as client:
        try:
            logger.debug("Making request to get object specs")
            response = client.get(f"{BASE_URL}/get_object_specs")
            response.raise_for_status()
            specs = response.json()
            # Return all specs without filtering
            logger.debug("Successfully retrieved object specs")
            return specs
        except httpx.RequestError as e:
            error_msg = f"Failed to get object specs: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error in get_deckhard_object_specs: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

@mcp.tool(name="list-deckhard_objects", description="List and filter objects of a specific type in the Deckhard system")
def list_deckhard_objects(object_type: str, properties_filter: Optional[Dict] = None, limit: Optional[int] = None) -> Dict:
    """List and filter objects of a specific type in the Deckhard system.
    
    Args:
        object_type: Type of objects to list (any valid object type in the Deckhard system)
        properties_filter: Optional dictionary of property filters. Supports exact matches and LIKE patterns.
            Examples:
            - Get object by ID: {"object_id": "agent_123"}
            - Get object by name: {"name": "My Agent"}
            - Pattern matching: {"name": {"operator": "like", "value": "%Test%"}}
            - Multiple filters: {"name": "Agent 1", "type": "analysis"}
        limit: Optional maximum number of objects to return
    
    Returns:
        Dictionary containing matched objects and metadata
    """
    logger.debug(f"list-deckhard_objects tool called for type {object_type}")
    
    # No longer validating object type against a predefined list
    
    with httpx.Client(timeout=30.0) as client:
        try:
            logger.debug(f"Making request to list {object_type} objects")
            params = {}
            if limit is not None:
                params['limit'] = limit
            if properties_filter is not None:
                params['properties_filter'] = properties_filter
            response = client.get(f"{BASE_URL}/objects/{object_type}", params=params)
            response.raise_for_status()
            logger.debug(f"Successfully retrieved {object_type} objects")
            return response.json()
        except httpx.RequestError as e:
            error_msg = f"Failed to list objects: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error in list-deckhard_objects: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

@mcp.tool(name="start_run_agent_task", description="Start an asynchronous agent run task")
async def start_run_agent_task(agent_id: str, properties: Optional[Dict] = None, dataset_id: Optional[str] = None, json_object_id: Optional[str] = None) -> str:
    """Start an asynchronous task to run an agent.
    
    Args:
        agent_id: ID of the agent to run
        properties: Optional dictionary of properties (highest priority)
        dataset_id: Optional ID of dataset to extract experiment description and data from
        json_object_id: Optional ID of JSON object to extract properties from
        
    Returns:
        Dictionary containing the task ID for checking status
    """
    logger.debug(f"start_run_agent_task called for agent {agent_id}")
    
    # Use a short timeout since we expect a quick response
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            logger.debug("Starting agent run task")
            params = {
                'dataset_id': dataset_id,
                'json_object_id': json_object_id
            }
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = await client.post(
                f"{BASE_URL}/agents/{agent_id}/start_run",
                params=params,
                json=properties
            )
            response.raise_for_status()
            
            # Parse and validate response
            try:
                data = response.json()
                logger.debug(f"Start task response raw: {response.text}")
                logger.debug(f"Start task response parsed: {data}")
                
                if not isinstance(data, dict) or 'task_id' not in data:
                    error_msg = "Invalid response format from start_run endpoint"
                    logger.error(f"{error_msg}: {data}")
                    return json.dumps({"error": error_msg})
                    
                # Return as properly formatted JSON string
                return json.dumps(data)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON response from start_run endpoint: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Response content: {response.text}")
                return json.dumps({"error": error_msg})
        except httpx.RequestError as e:
            error_msg = f"Failed to start agent run task: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error in start_run_agent_task: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

@mcp.tool(name="get_agent_task_status", description="Get the status of an agent run task")
async def get_agent_task_status(task_id: str) -> str:
    """Get the current status of an agent run task.
    
    Args:
        task_id: ID of the task to check
        
    Returns:
        Dictionary containing task status and result if complete
    """
    logger.debug(f"get_agent_task_status called for task {task_id}")
    
    # Use a short timeout since we expect a quick response
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            logger.debug("Getting task status")
            response = await client.get(f"{BASE_URL}/agent_tasks/{task_id}")
            response.raise_for_status()
            
            # Ensure we got a valid JSON response
            try:
                status_data = response.json()
                logger.debug(f"Task status response raw: {response.text}")
                logger.debug(f"Task status response parsed: {status_data}")
                
                # Return as properly formatted JSON string
                return json.dumps(status_data)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON response from task status endpoint: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Response content: {response.text}")
                return json.dumps({"error": error_msg})
                
        except httpx.RequestError as e:
            error_msg = f"Failed to get task status: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error in get_agent_task_status: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Error traceback: {traceback.format_exc()}")
            return {"error": error_msg}

@mcp.tool(name="create_deckhard_object", description="Create a new object in the Deckhard system")
def create_deckhard_object(object_type: str, properties: Dict) -> Dict:
    """Create a new object in the Deckhard system with the given properties.
    
    Args:
        object_type: Type of object to create (any valid object type in the Deckhard system)
        properties: Dictionary of property values. Missing properties will use defaults from the object spec.
        
    The server will validate properties and apply defaults based on the object specification.
    """
    logger.debug(f"create_deckhard_object tool called for type {object_type}")
    
    # No longer validating object type against a predefined list
    
    with httpx.Client() as client:
        try:
            logger.debug(f"Creating new {object_type} object")
            response = client.post(
                f"{BASE_URL}/objects/{object_type}/create",
                json=properties
            )
            response.raise_for_status()
            logger.debug("Successfully created object")
            return response.json()
        except httpx.RequestError as e:
            error_msg = f"Failed to create object: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error in create_deckhard_object: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

if __name__ == "__main__":
    logger.info("Starting Deckhard MCP server")
    mcp.run()
