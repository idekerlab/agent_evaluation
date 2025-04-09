import logging
import os
import json
import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri
from app.routes import agent_routes, object_routes, task_routes, knowledge_graph_routes
from app.ndex_utils import get_network_summary, get_complete_network  # Import our new utilities

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
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
base_dir = os.path.dirname(os.path.abspath(__file__))
# Mount our new static directory
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")

# Include routers - Add knowledge graph router first so its routes take precedence
app.include_router(knowledge_graph_routes)
app.include_router(object_routes)
app.include_router(task_routes)
app.include_router(agent_routes)

# NDEx API proxy endpoint
@app.get("/ndex-proxy/{path:path}")
async def ndex_proxy(path: str, request: Request):
    """Proxy for NDEx API requests to avoid CORS issues"""
    ndex_base_url = "https://www.ndexbio.org/v2"  # Use www subdomain
    url = f"{ndex_base_url}/{path}"
    
    # Get query parameters from the original request
    params = dict(request.query_params)
    
    # Log request details
    logger.info(f"NDEx proxy request received: PATH={path}")
    logger.info(f"Full URL to fetch: {url}")
    logger.info(f"Query parameters: {params}")
    
    try:
        # Use httpx for better async HTTP support
        async with httpx.AsyncClient(follow_redirects=True) as client:
            logger.info(f"Making request to NDEx: {url}")
            response = await client.get(url, params=params, timeout=30.0)
            
            # Log response details
            logger.info(f"NDEx response status: {response.status_code}")
            logger.info(f"NDEx response headers: {dict(response.headers)}")
            
            # If response is not successful, log the content for debugging
            if response.status_code >= 400:
                logger.error(f"Error response from NDEx: {response.text}")
            
            # Return the response data
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json")
            )
    except Exception as e:
        logger.error(f"Error proxying request to NDEx: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": f"Error connecting to NDEx API: {str(e)}"},
            status_code=500
        )

# NEW ENDPOINT: Direct NDEx client for fetching complete networks with nodes and edges
@app.get("/ndex-client/{uuid}")
async def get_ndex_network(uuid: str, summary_only: bool = False):
    """
    Get network from NDEx using the ndex2 client.
    
    Args:
        uuid: NDEx network UUID
        summary_only: If True, only fetch summary information (no nodes/edges)
        
    Returns:
        JSONResponse with network data
    """
    try:
        if summary_only:
            logger.info(f"Fetching network summary for UUID: {uuid}")
            data = get_network_summary(uuid)
        else:
            logger.info(f"Fetching complete network for UUID: {uuid}")
            data = get_complete_network(uuid)
            
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error fetching network from NDEx: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": f"Error fetching network from NDEx: {str(e)}"},
            status_code=500
        )

# New routes for our browser and reviewer pages
@app.get("/browser", response_class=HTMLResponse)
async def serve_browser_page():
    logger.info("Serving browser page")
    browser_path = os.path.join(base_dir, "static", "browser.html")
    try:
        with open(browser_path, "r") as file:
            content = file.read()
            return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error serving browser page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")

@app.get("/reviewer", response_class=HTMLResponse)
async def serve_reviewer_page():
    reviewer_path = os.path.join(base_dir, "static", "reviewer.html")
    if os.path.exists(reviewer_path):
        with open(reviewer_path, "r") as file:
            return HTMLResponse(file.read())
    return HTMLResponse("<h1>Reviewer page not available yet</h1>")

@app.get("/ndex-import", response_class=HTMLResponse)
async def serve_ndex_import_page():
    logger.info("Serving NDEx import page")
    ndex_import_path = os.path.join(base_dir, "static", "js", "ndex-import", "ndex-import.html")
    try:
        with open(ndex_import_path, "r") as file:
            content = file.read()
            return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error serving NDEx import page: {e}")
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>")

# Test endpoint for NDEx connectivity
@app.get("/test-ndex/{uuid}")
async def test_ndex_connection(uuid: str):
    """Test endpoint to check NDEx connectivity"""
    url = f"https://www.ndexbio.org/v2/network/{uuid}/summary"
    
    logger.info(f"Testing direct connection to NDEx: {url}")
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, timeout=30.0)
            
            logger.info(f"Direct NDEx test response status: {response.status_code}")
            
            if response.status_code >= 400:
                return JSONResponse(
                    content={"error": f"NDEx API error: {response.status_code}", "details": response.text},
                    status_code=response.status_code
                )
            
            # Return the actual JSON data from NDEx
            data = response.json()
            return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error testing NDEx connection: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": f"Error connecting to NDEx API: {str(e)}"},
            status_code=500
        )

# Sample data routes for testing
@app.get("/objects/object_list/{object_id}")
async def get_sample_object_list(object_id: str):
    """Return sample object list for testing the reviewer interface"""
    if object_id == "sample_object_list":
        sample_path = os.path.join(base_dir, "static", "sample_object_list.json")
        try:
            with open(sample_path, "r") as file:
                data = json.load(file)
                return JSONResponse({"object": data, "object_type": "object_list"})
        except Exception as e:
            logger.error(f"Error reading sample object list: {e}")
            return JSONResponse({"error": f"Error reading sample: {str(e)}"}, status_code=500)
    
    # Fall back to normal object_routes handler
    return {"error": "Object not found"}

@app.get("/objects/objects/{object_id}")
async def get_sample_object(object_id: str):
    """Return sample objects for testing the reviewer interface"""
    if object_id.startswith("sample_hypothesis_"):
        sample_path = os.path.join(base_dir, "static", f"{object_id}.json")
        try:
            if os.path.exists(sample_path):
                with open(sample_path, "r") as file:
                    data = json.load(file)
                    return JSONResponse({"object": data, "object_type": "hypothesis"})
        except Exception as e:
            logger.error(f"Error reading sample object: {e}")
            return JSONResponse({"error": f"Error reading sample: {str(e)}"}, status_code=500)
    
    # Fall back to normal object_routes handler
    return {"error": "Object not found"}

# Route for creating/updating reviews
@app.post("/objects/review/create")
async def create_sample_review(request: Request):
    """Create a sample review"""
    try:
        data = await request.json()
        # Generate a simple ID
        data["object_id"] = "sample_review_1"
        return JSONResponse(data)
    except Exception as e:
        logger.error(f"Error creating sample review: {e}")
        return JSONResponse({"error": f"Error creating review: {str(e)}"}, status_code=500)

@app.post("/objects/review/{review_id}/edit")
async def update_sample_review(review_id: str, request: Request):
    """Update a sample review (just returns success)"""
    try:
        # Just return success, we're not actually saving anything
        return JSONResponse({"success": True})
    except Exception as e:
        logger.error(f"Error updating sample review: {e}")
        return JSONResponse({"error": f"Error updating review: {str(e)}"}, status_code=500)

# Add a debug route to help diagnose issues
@app.get("/debug/paths")
async def debug_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    browser_path = os.path.join(static_dir, "browser.html")
    
    return {
        "base_dir": base_dir,
        "static_dir": static_dir,
        "static_dir_exists": os.path.exists(static_dir),
        "browser_path": browser_path,
        "browser_exists": os.path.exists(browser_path),
        "files_in_static": os.listdir(static_dir) if os.path.exists(static_dir) else []
    }

# Default route for the React app - must be last
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(full_path: str, request: Request):
    # Don't handle paths that should be handled by other routes
    if full_path.startswith("browser") or full_path.startswith("reviewer") or full_path.startswith("ndex-import") or full_path.startswith("static"):
        return HTMLResponse("<h1>Route not found</h1>")
        
    # Serve the index.html file for any route that doesn't match an API endpoint
    index_file_path = os.path.join(os.getcwd(), "react-app", "build", "index.html")
    if os.path.exists(index_file_path):
        with open(index_file_path, "r") as file:
            return HTMLResponse(file.read())
    return HTMLResponse("<h1>React app not available</h1>")
