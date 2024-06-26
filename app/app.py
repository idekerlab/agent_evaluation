# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import functools
from contextlib import asynccontextmanager
from app.sqlite_database import SqliteDatabase
from jsonschema import validate, ValidationError
from app.view_edit_specs import object_specifications
from app.config import load_database_config
import csv
from io import StringIO
import os
import json
from models.analysis_plan import AnalysisPlan
from models.review_plan import ReviewPlan
from services.analysisrunner import AnalysisRunner
from services.reviewrunner import ReviewRunner

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the database connection details
    _, uri, _, _ = load_database_config()
    db = SqliteDatabase(uri)
    
    # Provide the database instance to the app
    app.state.db = db

    yield

    # Shutdown
    db.close()

app = FastAPI(lifespan=lifespan)


# Setup templates and static files
base_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# # Setup templates and static files
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    object_types = list(object_specifications.keys())
    return templates.TemplateResponse("home.html", {"request": request, "object_types": object_types})

@app.get("/objects/{object_type}", response_class=HTMLResponse)
async def list_objects(request: Request, object_type: str):
    if object_type not in object_specifications:
        raise HTTPException(status_code=404, detail="Object type not found")
    db = request.app.state.db
    objects = db.find(object_type)  # Fetch all objects of the given type
    if object_type == 'hypothesis':
        for index, obj in enumerate(objects):
            analyst_id = obj['properties']['analyst_id']
            analyst_properties, analyst_type = db.load(analyst_id)
            objects[index]['properties']['analyst_id'] = f"({analyst_properties['name']}) {analyst_id}"
    
    return templates.TemplateResponse("object_list.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "objects": objects})

def preprocess_properties(properties, object_type):
    for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
        if prop_spec.get('type') == 'csv' and properties.get(prop_name):
            csv_data = StringIO(properties[prop_name])
            reader = csv.reader(csv_data)
            rows = list(reader)
            properties[prop_name] = rows
    return properties

# get the view page with the object and its properties
@app.get("/objects/{object_type}/{object_id}", response_class=HTMLResponse)
async def view_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, object_type = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    # Preprocess CSV data
    processed_properties = preprocess_properties(properties, object_type)
    
    # Process object links to include object names
    link_names = {}
    for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
        if prop_name != 'object_id' and prop_name != 'created' and prop_name != 'name' and prop_name in processed_properties:
            if prop_spec['view'] == 'object_link':
                obj_id = processed_properties[prop_name]
                try:
                    linked_object_properties, linked_object_type = db.load(processed_properties[prop_name])
                    if "name" in linked_object_properties:
                        link_names[obj_id] = linked_object_properties['name'] if len(linked_object_properties['name']) > 0 else "unnamed"
                    else:
                        link_names[obj_id] = "unnamed"
                except Exception as e:
                    link_names[obj_id] = "Invalid ID"
                
            elif prop_spec['view'] == 'list_of_object_links':
                for obj_id in processed_properties[prop_name]:
                    try:
                        linked_object_properties, linked_object_type = db.load(obj_id)
                        if "name" in linked_object_properties:
                            link_names[obj_id] = linked_object_properties['name'] if len(linked_object_properties['name']) > 0 else "unnamed"
                        else:
                            link_names[obj_id] = "unnamed"
                    except Exception as e:
                        link_names[obj_id] = "Invalid ID"
                        
    return templates.TemplateResponse("view_object.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "object": processed_properties,
                                                           "object_spec": object_specifications[object_type],
                                                           "link_names": link_names})

# get the edit page with a new object of the same type and default properties
@app.get("/objects/{object_type}/blank/new", response_class=HTMLResponse)
async def new_object(request: Request, object_type: str):
    db = request.app.state.db
    default_properties = get_default_properties(object_type, object_specifications)
    new_object_id , new_properties, _ = db.add(object_id=None, properties=default_properties, object_type=object_type)
    new_properties["object_id"] = new_object_id
    new_properties["name"] = f"{object_type} {new_properties['created']}"
    form_fields = generate_form(db, object_type, object_specifications, new_properties)
    return templates.TemplateResponse("edit_object.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "object": new_properties, 
                                                           "form_fields": form_fields,
                                                           "object_spec": object_specifications[object_type]})

def get_default_properties(object_type, specifications):
    default_properties = {}
    for field_name, field_spec in specifications[object_type]["properties"].items():
        default_properties[field_name] = field_spec.get("default", "")
    return default_properties

# get the edit page with an existing object and its properties
@app.get("/objects/{object_type}/{object_id}/edit", response_class=HTMLResponse)
async def edit_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, _ = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    form_fields = generate_form(db, object_type, object_specifications, properties)
    return templates.TemplateResponse("edit_object.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "object": properties, 
                                                           "form_fields": form_fields,
                                                           "object_spec": object_specifications[object_type]})

# get the edit page with a new object of the same type and same properties
@app.get("/objects/{object_type}/{object_id}/clone", response_class=HTMLResponse)
async def clone_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, _ = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    properties.pop('object_id', None)
    cloned_object_id, cloned_properties, _ = db.add(object_id=None, properties=properties, object_type=object_type)
    cloned_properties["object_id"] = cloned_object_id
    cloned_properties["name"] = f"{object_type} {cloned_properties['created']}"
    form_fields = generate_form(db, object_type, object_specifications, cloned_properties)
    return templates.TemplateResponse("edit_object.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "object": cloned_properties, 
                                                           "form_fields": form_fields,
                                                           "object_spec": object_specifications[object_type]})


# make the form fields based on the object type and its properties
def generate_form(db, object_type, specifications, obj_properties):
    fields = []

    # Ensure the object_type exists in the specifications
    if object_type not in specifications:
        print(f"Error: '{object_type}' is not a valid object type in specifications.")
        return fields

    # Get the specific specifications for the given object_type
    object_spec = specifications[object_type]

    for field_name, field_spec in object_spec["properties"].items():
        try:
            if (field_spec.get("input_type", "") == "select_single_object" 
                or field_spec.get("input_type", "") == "select_multiple_objects"):
                field_object_type = field_spec.get("object_type", "")
                field_objects = db.find(field_object_type)
                option_dicts = []
                for field_object in field_objects:
                    field_obj_id = field_object['object_id']
                    field_obj_name = field_object['properties']['name'] if 'name' in field_object['properties'] else "none"
                    field_obj_name = field_obj_name if len(field_obj_name) > 0 else "none"
                    option_label = f"({field_obj_name}) {field_obj_id}"
                    option_dicts.append({"label": option_label, "value": field_obj_id})
                    
                field_spec["options"] = option_dicts

            field = {
                "name": field_name,
                "type": field_spec.get("type", "text"),  # Default to "text
                "label": field_spec.get("label") or field_name.replace('_', ' '),
                "input_type": field_spec.get("input_type", "text"),
                "value": obj_properties.get(field_name, field_spec.get("default", "")),
                "options": field_spec.get("options", []),
                "editable": field_spec["editable"],
                "view": field_spec.get("view", "text"),
                "conditional_on": field_spec.get("conditional_on", None),
                "min": field_spec.get("min", ""),
                "max": field_spec.get("max", ""),
                "step": field_spec.get("step", ""),
                "regex": field_spec.get("regex", ""),
                "regex_description": field_spec.get("regex_description", "")
            }
            fields.append(field)
        except KeyError as e:
            print(f"Error in field specification for '{field_name}': missing key {e}")
        except Exception as e:
            print(f"Unexpected error in field specification for '{field_name}': {e}")

    return fields

from fastapi import HTTPException

# receive the form data and update the object, redirect to the view page
@app.post("/objects/{object_type}/{object_id}/edit", response_class=HTMLResponse)
async def update_object(request: Request, object_type: str, object_id: str):
    form_data = await request.form()
    form_data = dict(form_data)
    # Ensure the object_type exists in the specifications
    if object_type not in object_specifications:
        print(f"Error: '{object_type}' is not a valid object type in specifications.")
        return form_data

    # Get the specific specifications for the given object_type
    object_spec = object_specifications[object_type]
    # Process the form data to handle list_of_object_ids
    for field_name, field_spec in object_spec["properties"].items():
        if field_spec.get("type") == "list_of_object_ids":
            id_list = form_data.get(field_name).replace("'", '"')
            id_list = json.loads(id_list) 
            form_data[field_name] = id_list
    db = request.app.state.db
    try:
        await handle_form_submission(form_data, object_type, db)
        return RedirectResponse(url=f"/objects/{object_type}/{object_id}", status_code=303)
    except FormSubmissionError as e:
        # Return an error response to the web app
        return HTMLResponse(content=f"<h1>Error</h1><p>{e.message}</p>", status_code=400)
    except Exception as e:
        # Return a generic error response
        return HTMLResponse(content="<h1>Unexpected Error</h1><p>Something went wrong.</p>", status_code=500)

# receive the form data and update the object, redirect to the view page
@app.post("/objects/{object_type}/{object_id}/new", response_class=HTMLResponse)
async def update_object(request: Request, object_type: str, object_id: str):
    form_data = await request.form()
    form_data = dict(form_data)
    
    # Get the specific specifications for the given object_type
    object_spec = object_specifications[object_type]
    # Process the form data to handle list_of_object_ids
    for field_name, field_spec in object_spec["properties"].items():
        if field_spec.get("type") == "list_of_object_ids":
            id_list = form_data.get(field_name).replace("'", '"')
            id_list = json.loads(id_list) if id_list else []
            form_data[field_name] = id_list
            
    db = request.app.state.db
    try:
        await handle_form_submission(form_data, object_type, db)
        object_id_from_form = form_data.get("object_id")
        return RedirectResponse(url=f"/objects/{object_type}/{object_id_from_form}", status_code=303)
    except FormSubmissionError as e:
        # Return an error response to the web app
        return HTMLResponse(content=f"<h1>Error</h1><p>{e.message}</p>", status_code=400)
    except Exception as e:
        # Return a generic error response
        return HTMLResponse(content="<h1>Unexpected Error</h1><p>Something went wrong.</p>", status_code=500)
    

# receive the form data and update the object, redirect to the view page
@app.post("/objects/{object_type}/{object_id}/clone", response_class=HTMLResponse)
async def update_object(request: Request, object_type: str, object_id: str):
    form_data = await request.form()
    form_data = dict(form_data)
    
    # Get the specific specifications for the given object_type
    object_spec = object_specifications[object_type]
    # Process the form data to handle list_of_object_ids
    for field_name, field_spec in object_spec["properties"].items():
        if field_spec.get("type") == "list_of_object_ids":
            id_list = form_data.get(field_name).replace("'", '"')
            id_list = json.loads(id_list) if id_list else []
            form_data[field_name] = id_list
            
    db = request.app.state.db
    try:
        await handle_form_submission(form_data, object_type, db)
        object_id_from_form = form_data.get("object_id")
        return RedirectResponse(url=f"/objects/{object_type}/{object_id_from_form}", status_code=303)
    except FormSubmissionError as e:
        # Return an error response to the web app
        return HTMLResponse(content=f"<h1>Error</h1><p>{e.message}</p>", status_code=400)
    except Exception as e:
        # Return a generic error response
        return HTMLResponse(content="<h1>Unexpected Error</h1><p>Something went wrong.</p>", status_code=500)
    
@app.post("/objects/{object_type}/{object_id}/delete", response_class=HTMLResponse)
async def delete_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    db.remove(object_id)
    return RedirectResponse(url=f"/objects/{object_type}", status_code=303)
    
def validate_form_data(data, specifications):
    # The schema should be wrapped in a proper JSON schema format
    schema = {
        "type": "object",
        "properties": specifications["properties"],
        "required": [key for key, value in specifications["properties"].items() if value.get("required", False)]
    }
    validate(instance=data, schema=schema)
    
@app.post("/objects/{object_type}/{object_id}/execute", response_class=HTMLResponse)
async def execute_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    
    if object_type == "analysis_plan":
        analysis_plan = AnalysisPlan.load(db, object_id)
        analysis_run = analysis_plan.generate_analysis_run()
        
        
        def execute_analysis_plan(analysis_run_id):
            _, uri, _, _ = load_database_config()
            db = SqliteDatabase(uri)
            runner = AnalysisRunner(db, analysis_run_id)
            result = runner.run()
            return result
        
        loop = asyncio.get_event_loop()
        runner_func = functools.partial(execute_analysis_plan, analysis_run.object_id)
        result = await loop.run_in_executor(None, runner_func)
        return RedirectResponse(url=f"/objects/{object_type}/{analysis_run.object_id}", status_code=303)
    
    elif object_type == "review_plan":
        review_plan = ReviewPlan.load(db, object_id)
        review_set = review_plan.generate_review_set()
        
        
        def execute_review_plan(review_set_id):
            _, uri, _, _ = load_database_config()
            db = SqliteDatabase(uri)
            runner = ReviewRunner(db, review_set_id)
            result = runner.run()
            return result
        
        loop = asyncio.get_event_loop()
        runner_func = functools.partial(execute_review_plan, review_set.object_id)
        result = await loop.run_in_executor(None, runner_func)
        return RedirectResponse(url=f"/objects/{object_type}/{review_set.object_id}", status_code=303)
        

class FormSubmissionError(Exception):
    """Custom exception for form submission errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

async def handle_form_submission(form_data, object_type, db):
    try:
        # Extract CSV file from form data
        csv_file = form_data.pop('data', None) if object_type == "dataset" else None
        if csv_file:
            # Read the contents of the CSV file as text
            #csv_content = csv_file.read().decode('utf-8')
            csv_content = (await csv_file.read()).decode('utf-8')
            # Include the CSV text data in form_data
            form_data['data'] = csv_content
        
        if form_data.get("object_id"):
            db.update(form_data["object_id"], form_data)
        else:
            # db.add(object_id=None, properties=form_data, object_type=object_type)
            raise Exception("No object_id provided in form data")
    except ValidationError as e:
        raise FormSubmissionError(f"Form data validation failed: {e.message}")
    except Exception as e:
        raise FormSubmissionError(f"An error occurred while processing the form: {e}")
