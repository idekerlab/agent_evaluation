import logging
import json
import asyncio
import functools
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Request, Query, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from app.view_edit_specs import object_specifications
from app.sqlite_database import SqliteDatabase
from app.config import load_database_uri
from models.analysis_plan import AnalysisPlan
from models.review_plan import ReviewPlan
from services.analysisrunner import AnalysisRunner
from services.reviewrunner import ReviewRunner
from app.handlers.form_handlers import (
    generate_form,
    handle_form_submission,
    get_default_properties,
    FormSubmissionError
)
from app.handlers.file_handlers import (
    preprocess_properties,
    process_object_links,
    handle_hypothesis,
    generate_judgment_space_visualization,
    convert_to_csv
)
from models.judgment_space import JudgmentSpace
from helpers.json_to_markdown import json_to_markdown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["objects"])

@router.post("/objects/{object_type}/create")
async def create_simple_object(object_type: str, request: Request, properties: Dict = Body(...)):
    """Simple object creation endpoint that handles validation and defaults."""
    
    try:
        db = request.app.state.db
        
        # Check if the object type is defined in view_edit_specs
        if object_type in object_specifications:
            # Get the specification for this object type
            spec = object_specifications[object_type]
            
            # Fill in defaults for missing properties
            for prop_name, prop_spec in spec["properties"].items():
                if prop_name not in properties and "default" in prop_spec:
                    properties[prop_name] = prop_spec["default"]
        else:
            # For object types not defined in view_edit_specs, don't add defaults
            logger.info(f"Creating object of type '{object_type}' with flexible properties (type not in object_specifications)")
        
        # Add to database
        object_id, created_properties, _ = db.add(object_id=None, properties=properties, object_type=object_type)
        created_properties["object_id"] = object_id
        
        return created_properties
    except Exception as e:
        logger.error(f"Error creating object of type '{object_type}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_object_specs")
async def return_object_specs(request: Request):
    logger.info("Fetching object specifications")
    try:
        return object_specifications
    except Exception as e:
        logger.error(f"Error returning object specifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get object specifications: {str(e)}")

@router.get("/objects/{object_type}")
async def list_objects(
    request: Request, 
    object_type: str,
    limit: Optional[int] = Query(None, ge=1, description="Maximum number of objects to return"),
    properties_filter: Optional[Dict] = None
):
    logger.info(f"Listing objects of type: {object_type}, filter: {properties_filter}")
    
    db = request.app.state.db
    try:
        # Handle special case for user objects
        if object_type == "user":
            objects = db.find("user", properties_filter)
        else:
            objects = db.find(object_type, properties_filter)
            
        logger.info(f"Found {len(objects)} objects of type {object_type}")
        if len(objects) == 0:
            logger.warning(f"No objects found for type {object_type}")
    except Exception as e:
        logger.error(f"Database error fetching {object_type} objects: {str(e)}")
        return {"error": f"Failed to fetch objects: {str(e)}"}
    
    if object_type == 'hypothesis':
        for index, obj in enumerate(objects):
            if ("agent_id" in obj['properties']):
                agent_id = obj['properties']['agent_id']
                agent_properties, agent_type = db.load(agent_id)
                if agent_properties:
                    objects[index]['properties']['agent_id'] = f"({agent_properties['name']}) {agent_id}"
    
    # Apply limit after hypothesis processing
    if limit:
        objects = objects[:limit]
            
    objects.reverse()
    
    # Use object specifications if available, otherwise return empty object
    object_spec = object_specifications.get(object_type, {})
    
    return {
        "object_type": object_type, 
        "objects": objects, 
        "object_spec": object_spec,
        "total_count": len(objects)
    }

@router.get("/objects/{object_type}/{object_id}")
async def view_object(request: Request, object_type: str, object_id: str):
    logger.info(f"Viewing object: {object_id} of type {object_type}")
    db = request.app.state.db
    try:
        properties, loaded_type = db.load(object_id)
        if not properties:
            logger.error(f"Object not found: {object_id}")
            raise HTTPException(status_code=404, detail="Object not found")
        if loaded_type != object_type and object_type != "objects":
            logger.warning(f"Type mismatch: requested {object_type}, got {loaded_type}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading object {object_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load object: {str(e)}")
    
    try:
        # Only process properties if the object type is in object_specifications
        processed_properties = properties
        link_names = {}
        
        if object_type in object_specifications:
            processed_properties = preprocess_properties(properties, object_type, object_specifications)
            link_names = process_object_links(db, processed_properties, object_specifications, object_type)
            
            if object_type == "hypothesis":
                processed_properties = handle_hypothesis(processed_properties)
        
        visualizations = {}
    except Exception as e:
        logger.error(f"Error processing object {object_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process object: {str(e)}")
    
    if object_type == "json":
        # Add markdown representation for Json objects
        processed_properties["markdown"] = json_to_markdown(processed_properties["json"])
    
    if object_type == "judgment_space":
        judgment_space = JudgmentSpace.load(db, object_id)
        # When viewing a JudgmentSpace, we generate the visualizations on the fly.
        # This way, they update with any changes to the JS, such as adding more
        # reviewers. They are updated to the database because that causes them
        # to be loaded to the view page like any other object data.
        if judgment_space:
            try:
                visualizations = judgment_space.generate_visualizations()
                processed_properties['visualizations'] = visualizations
                judgment_space.update(visualizations=visualizations)
            except Exception as e:
                error_message = f"Error generating visualizations: {str(e)}"
                processed_properties['visualization_error'] = error_message
                visualizations = {'error': error_message}
    
    # Use object specifications if available, otherwise return empty object
    object_spec = object_specifications.get(object_type, {})
    
    return {
        "object_type": object_type, 
        "object": processed_properties,
        "object_spec": object_spec,
        "link_names": link_names,
        "visualizations": visualizations
    }

@router.get("/objects/{object_type}/blank/new")
async def new_object(request: Request, object_type: str):
    db = request.app.state.db
    
    # Check if the object type is defined in object_specifications
    if object_type in object_specifications:
        default_properties = get_default_properties(object_type, object_specifications)
        form_fields = generate_form(db, object_type, object_specifications, default_properties)
    else:
        # For object types not in specifications, provide minimal defaults
        default_properties = {}
        form_fields = []
    
    new_object_id, new_properties, _ = db.add(object_id=None, properties=default_properties, object_type=object_type)
    new_properties["object_id"] = new_object_id
    
    if "name" not in new_properties and "created" in new_properties:
        new_properties["name"] = f"{object_type} {new_properties['created']}"
    
    db.remove(new_object_id)
    
    # Use object specifications if available, otherwise return empty object
    object_spec = object_specifications.get(object_type, {})
    
    return {
        "object_type": object_type, 
        "object": new_properties, 
        "form_fields": form_fields,
        "object_spec": object_spec
    }

@router.get("/objects/{object_type}/{object_id}/edit")
async def edit_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, _ = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    
    # Check if the object type is defined in object_specifications
    form_fields = []
    if object_type in object_specifications:
        form_fields = generate_form(db, object_type, object_specifications, properties)
    
    # Use object specifications if available, otherwise return empty object
    object_spec = object_specifications.get(object_type, {})
    
    return {
        "object_type": object_type, 
        "object": properties, 
        "form_fields": form_fields,
        "object_spec": object_spec
    }

@router.get("/objects/{object_type}/{object_id}/clone")
async def clone_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, _ = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    properties.pop('object_id', None)
    
    if "name" in properties:
        properties["name"] = f"{properties['name']} - Cloned"
    
    cloned_object_id, cloned_properties, _ = db.add(object_id=None, properties=properties, object_type=object_type)
    
    return {"object_id": cloned_object_id}

@router.post("/objects/{object_type}/{object_id}/edit", response_class=HTMLResponse)
async def update_object(request: Request, object_type: str, object_id: str):
    logger.info(f"Updating object: {object_id} of type {object_type}")
    
    # First, attempt to get JSON data if the content type is application/json
    try:
        if request.headers.get("content-type") == "application/json":
            form_data = await request.json()
            logger.debug(f"Received JSON data: {form_data}")
            
            # Ensure object_id is in the form data
            if "object_id" not in form_data:
                form_data["object_id"] = object_id
                
            db = request.app.state.db
            
            # For objects not in specifications, handle direct update
            if object_type not in object_specifications:
                # Make sure we have the object_id in the data
                properties, _ = db.load(object_id)
                if not properties:
                    raise HTTPException(status_code=404, detail="Object not found")
                
                # Update properties
                db.update(object_id, form_data)
                return RedirectResponse(url=f"/objects/{object_type}/{object_id}", status_code=303)
            else:
                # Use the form handler for specified objects
                await handle_form_submission(form_data, object_type, db)
                return RedirectResponse(url=f"/objects/{object_type}/{object_id}", status_code=303)
        else:
            # Process form data if not JSON
            form_data = await request.form()
            form_data = dict(form_data)
            logger.debug(f"Received form data: {form_data}")
            
            # Ensure object_id is in the form data
            if "object_id" not in form_data:
                form_data["object_id"] = object_id
            
            db = request.app.state.db
            
            # Check if the object type is defined in object_specifications
            if object_type in object_specifications:
                # Get the specific specifications for the given object_type
                object_spec = object_specifications[object_type]
                # Process the form data to handle list_of_object_ids
                for field_name, field_spec in object_spec["properties"].items():
                    if field_spec.get("type") == "list_of_object_ids" and field_name in form_data:
                        id_list = form_data[field_name].replace("'", '"')
                        id_list = json.loads(id_list) 
                        form_data[field_name] = id_list
                    if field_spec.get("editable") == False:
                        form_data.pop(field_name, None)
            
            # Process specific data types for non-specified objects
            if object_type not in object_specifications:
                # Handle scores as JSON if present
                if "scores" in form_data and isinstance(form_data["scores"], str):
                    try:
                        form_data["scores"] = json.loads(form_data["scores"])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse scores as JSON: {form_data['scores']}")
                
                # Handle object_ids as JSON if present
                if "object_ids" in form_data and isinstance(form_data["object_ids"], str):
                    try:
                        form_data["object_ids"] = json.loads(form_data["object_ids"])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse object_ids as JSON: {form_data['object_ids']}")
            
            if object_type in object_specifications:
                await handle_form_submission(form_data, object_type, db)
            else:
                # For object types not in specifications, handle basic update
                properties, _ = db.load(object_id)
                if not properties:
                    raise HTTPException(status_code=404, detail="Object not found")
                
                # Update properties with form data
                for key, value in form_data.items():
                    properties[key] = value
                
                db.update(object_id, properties)
                
            return RedirectResponse(url=f"/objects/{object_type}/{object_id}", status_code=303)
    except FormSubmissionError as e:
        # Return an error response to the web app
        return HTMLResponse(content=f"<h1>Error</h1><p>{e.message}</p>", status_code=400)
    except Exception as e:
        logger.error(f"Error updating object: {str(e)}")
        # Return a generic error response
        return HTMLResponse(content="<h1>Unexpected Error</h1><p>Something went wrong.</p>", status_code=500)

@router.post("/objects/{object_type}/{object_id}/new")
async def create_new_object(request: Request, object_type: str, object_id: str):
    form_data = await request.form()
    form_data = dict(form_data)
    
    db = request.app.state.db
    
    # Check if the object type is defined in object_specifications
    if object_type in object_specifications:
        # Get the specific specifications for the given object_type
        object_spec = object_specifications[object_type]
        # Process the form data to handle list_of_object_ids
        for field_name, field_spec in object_spec["properties"].items():
            if field_spec.get("type") == "list_of_object_ids":
                id_list = form_data.get(field_name).replace("'", '"')
                id_list = json.loads(id_list) if id_list else []
                form_data[field_name] = id_list
        
        default_properties = get_default_properties(object_type, object_specifications)
    else:
        # For object types not in specifications, use empty defaults
        default_properties = {}
    
    new_object_id, new_properties, _ = db.add(object_id=None, properties=default_properties, object_type=object_type)
    form_data["object_id"] = new_object_id
    
    try:
        if object_type in object_specifications:
            await handle_form_submission(form_data, object_type, db)
        else:
            # For object types not in specifications, handle basic creation
            for key, value in form_data.items():
                if key != "object_id":
                    new_properties[key] = value
            
            db.update(new_object_id, new_properties)
        
        object_id_from_form = form_data.get("object_id", new_object_id)
        return {"object_id": object_id_from_form}
    except FormSubmissionError as e:
        # Clean up the new object if there's an error
        db.remove(new_object_id)
        # Return an error response to the web app
        return HTMLResponse(content=f"<h1>Error</h1><p>{e.message}</p>", status_code=400)
    except Exception as e:
        # Clean up the new object if there's an error
        db.remove(new_object_id)
        logger.error(f"Error creating new object: {str(e)}")
        # Return a generic error response
        return HTMLResponse(content="<h1>Unexpected Error</h1><p>Something went wrong.</p>", status_code=500)

@router.post("/objects/{object_type}/{object_id}/delete", response_class=HTMLResponse)
async def delete_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    db.remove(object_id)
    return RedirectResponse(url=f"/objects/{object_type}", status_code=303)

@router.post("/objects/{object_type}/{object_id}/execute")
async def execute_object(request: Request, object_type: str, object_id: str):
    """Execute a plan object (analysis_plan or review_plan)."""
    logger.info(f"Executing {object_type} with ID: {object_id}")
    
    if object_type not in ["analysis_plan", "review_plan"]:
        raise HTTPException(status_code=400, detail=f"Cannot execute object of type {object_type}")
    
    db = request.app.state.db
    
    if object_type == "analysis_plan":
        analysis_plan = AnalysisPlan.load(db, object_id)
        
        try:
            analysis_run = analysis_plan.generate_analysis_run()
        except Exception as e:
            return {"error": f"{e}"}
        
        def execute_analysis_plan(analysis_run_id):
            uri = load_database_uri()
            db = SqliteDatabase(uri)
            runner = AnalysisRunner(db, analysis_run_id)
            result = runner.run()
            return result
        
        loop = asyncio.get_event_loop()
        runner_func = functools.partial(execute_analysis_plan, analysis_run.object_id)
        result = await loop.run_in_executor(None, runner_func)
        return {"url": f"/objects/{object_type}/{analysis_run.object_id}"}
    
    elif object_type == "review_plan":
        review_plan = ReviewPlan.load(db, object_id)
        
        try:
            review_set = review_plan.generate_review_set()
        except Exception as e:
            return {"error": f"{e}"}
        
        def execute_review_plan(review_set_id):
            uri = load_database_uri()
            db = SqliteDatabase(uri)
            runner = ReviewRunner(db, review_set_id)
            result = runner.run()
            return result
        
        loop = asyncio.get_event_loop()
        runner_func = functools.partial(execute_review_plan, review_set.object_id)
        result = await loop.run_in_executor(None, runner_func)
        return {"url": f"/objects/{object_type}/{review_set.object_id}"}
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Execution not supported for object type: {object_type}"
        )

@router.post("/objects/{object_type}/import")
async def import_object(request: Request, object_type: str):
    form_data = await request.form()
    form_data = dict(form_data)
    
    db = request.app.state.db
    
    json_file = form_data.pop('json', None)
    if json_file:
        json_content = (await json_file.read()).decode('utf-8')
        json_obj = json.loads(json_content)
        
        # Check if the object type is defined in object_specifications
        if object_type in object_specifications:
            default_properties = get_default_properties(object_type, object_specifications)
        else:
            # For object types not in specifications, use empty defaults
            default_properties = {}
        
        new_object_id, new_properties, _ = db.add(object_id=None, properties=default_properties, object_type=object_type)
        json_obj["object_id"] = new_object_id
        
        # Handle CSV data conversion if the object has it
        if "data" in json_obj and object_type in object_specifications:
            if object_specifications[object_type]["properties"].get("data", {}).get("type") == "csv":
                json_obj["data"] = convert_to_csv(json_obj['data'])
        
        try:
            if object_type in object_specifications:
                await handle_form_submission(json_obj, object_type, db)
            else:
                # For object types not in specifications, handle basic import
                for key, value in json_obj.items():
                    if key != "object_id":
                        new_properties[key] = value
                
                db.update(new_object_id, new_properties)
            
            return {"object_id": new_object_id}
        except FormSubmissionError as e:
            # Clean up the new object if there's an error
            db.remove(new_object_id)
            logger.error(f"Form submission error: {e.message}")
            return HTMLResponse(content=f"<h1>Form Submission Error</h1><p>{e.message}</p>", status_code=400)
        except Exception as e:
            # Clean up the new object if there's an error
            db.remove(new_object_id)
            logger.error(f"Unexpected error during import: {str(e)}")
            return HTMLResponse(content="<h1>Unexpected Error</h1><p>Something went wrong.</p>", status_code=500)
        
    return {"error": "Something went wrong"}