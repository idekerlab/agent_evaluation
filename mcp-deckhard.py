from fastmcp import FastMCP
import requests
import json
from typing import Optional, Dict, Any, List, Union
from enum import Enum

# Create an MCP server
mcp = FastMCP("Deckhard")

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust to match your Deckhard server

# Define allowed object types
class ObjectType(str, Enum):
    AGENT = "agent"
    LLM = "llm"
    DATASET = "dataset"
    JSON = "json"

@mcp.tool()
def get_object_specs() -> Dict:
    """Get specifications for all object types in the Deckhard AI research workflow management system.
    Returns specifications for agents (LLM interaction templates), LLMs (language model configurations),
    datasets (structured input data), and JSON objects (generic input/output storage)."""
    try:
        response = requests.get(f"{BASE_URL}/get_object_specs")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        specs = response.json()
        return {k: v for k, v in specs.items() if k in [e.value for e in ObjectType]}
    except requests.RequestException as e:
        return {"error": f"Failed to get object specs: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def list_objects(object_type: ObjectType, limit: Optional[int] = None) -> Dict:
    """List objects of a specific type in the Deckhard AI research workflow management system, 
    optionally limited to a maximum number. Valid types are:
    - agent: Templates for LLM interactions with specific prompts/contexts
    - llm: Language model configurations (GPT-4, Claude, etc.)
    - dataset: Structured data inputs for analysis
    - json: Generic storage for any JSON-formatted data"""
    try:
        params = {'limit': limit} if limit is not None else {}
        response = requests.get(f"{BASE_URL}/objects/{object_type}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to list objects: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def get_object(object_type: ObjectType, object_id: str) -> Dict:
    """Get a specific object by type and ID from the Deckhard AI research workflow management system.
    The object_type must be one of: agent (LLM templates), llm (model configs), 
    dataset (input data), or json (generic storage)."""
    try:
        response = requests.get(f"{BASE_URL}/objects/{object_type}/{object_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to get object: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def create_object(object_type: ObjectType, properties: Dict[str, Any]) -> Dict:
    """Create a new object in the Deckhard AI research workflow management system.
    The object_type determines what kind of resource to create:
    - agent: New LLM interaction template with specific prompts/contexts
    - llm: New language model configuration
    - dataset: New structured data input
    - json: New generic JSON storage object
    
    Properties should match the specifications for the chosen object type."""
    try:
        response = requests.post(f"{BASE_URL}/objects/{object_type}/new", json=properties)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to create object: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def update_object(object_type: ObjectType, object_id: str, properties: Dict[str, Any]) -> Dict:
    """Update an existing object in the Deckhard AI research workflow management system.
    The object_type must be one of:
    - agent: Modify LLM interaction template settings
    - llm: Update language model configuration
    - dataset: Revise structured data input
    - json: Update stored JSON data
    
    Properties should match the specifications for the chosen object type."""
    try:
        response = requests.post(f"{BASE_URL}/objects/{object_type}/{object_id}/edit", json=properties)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to update object: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def delete_object(object_type: ObjectType, object_id: str) -> Dict:
    """Delete an object from the Deckhard AI research workflow management system.
    Permanently removes the specified object of type:
    - agent: LLM interaction template
    - llm: Language model configuration
    - dataset: Structured data input
    - json: Generic JSON storage object"""
    try:
        response = requests.post(f"{BASE_URL}/objects/{object_type}/{object_id}/delete")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to delete object: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# Resource for getting object by ID
@mcp.resource("object://{object_type}/{object_id}")
def get_object_resource(object_type: ObjectType, object_id: str) -> Dict:
    """Get an object resource by its type and ID from the Deckhard AI research workflow management system.
    The object_type must be one of: agent (LLM templates), llm (model configs), 
    dataset (input data), or json (generic storage)."""
    try:
        return get_object(object_type, object_id)
    except Exception as e:
        return {"error": f"Failed to get object resource: {str(e)}"}

@mcp.tool()
def project_info() -> Dict[str, str]:
    """Get information about the Deckhard AI research workflow management system.
    This tool provides a static description of the system's purpose and capabilities
    without making any network requests."""
    return {
        "name": "Deckhard",
        "description": "An AI research workflow management system for hypothesis generation and evaluation",
        "core_features": [
            "LLM integration and configuration management",
            "Agent-based hypothesis generation",
            "Structured data management",
            "Generic JSON object storage"
        ],
        "main_components": {
            "agents": "Templates for LLM interactions with specific prompts and contexts",
            "llms": "Language model configurations for various providers (GPT-4, Claude, etc.)",
            "datasets": "Structured data inputs for analysis",
            "json_objects": "Generic storage for JSON-formatted data"
        },
        "version": "1.0.0",
        "documentation": "The system provides a REST API (port 8000) and React-based UI (port 3000) for managing AI research workflows"
    }

if __name__ == "__main__":
    mcp.run() 