# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
#from app.database import Database  # Import your existing Database class
from app.sqlite_database import SqliteDatabase
from jsonschema import validate, ValidationError
from app.view_edit_specs import object_specifications
from app.config import load_database_config
import csv
from io import StringIO
import os


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
    return templates.TemplateResponse("object_list.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "objects": objects})

@app.get("/objects/new/{object_type}", response_class=HTMLResponse)
async def new_object(request: Request, object_type: str):
    form_fields = generate_form(object_type, object_specifications, {})
    return templates.TemplateResponse("new_object.html", {
        "request": request,
        "object_type": object_type,
        "form_fields": form_fields
    })

@app.post("/objects/new/{object_type}", response_class=HTMLResponse)
async def create_object(request: Request, object_type: str):
    form_data = await request.form()
    form_data = dict(form_data)
    db = request.app.state.db
    handle_form_submission(form_data, object_type, db)
    return RedirectResponse(url=f"/objects/{object_type}", status_code=303)

@app.get("/objects/{object_type}/{object_id}", response_class=HTMLResponse)
async def view_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, object_type = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    # Preprocess CSV data
    for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
        if prop_spec.get('type') == 'csv' and properties.get(prop_name):
            csv_data = StringIO(properties[prop_name])
            reader = csv.reader(csv_data)
            rows = list(reader)
            properties[prop_name] = rows
    return templates.TemplateResponse("view_object.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "object": properties,
                                                           "object_spec": object_specifications[object_type]})

@app.get("/objects/{object_type}/{object_id}/edit", response_class=HTMLResponse)
async def edit_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, _ = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    form_fields = generate_form(object_type, object_specifications, properties)
    return templates.TemplateResponse("edit_object.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "object": properties, 
                                                           "form_fields": form_fields,
                                                           "object_spec": object_specifications[object_type]})

@app.post("/objects/{object_type}/{object_id}/edit", response_class=HTMLResponse)
async def update_object(request: Request, object_type: str, object_id: str):
    form_data = await request.form()
    form_data = dict(form_data)
    db = request.app.state.db
    handle_form_submission(form_data, object_type, db)
    return RedirectResponse(url=f"/objects/{object_type}/{object_id}", status_code=303)

def generate_form(object_type, specifications, obj_properties):
    fields = []

    # Ensure the object_type exists in the specifications
    if object_type not in specifications:
        print(f"Error: '{object_type}' is not a valid object type in specifications.")
        return fields

    # Get the specific specifications for the given object_type
    object_spec = specifications[object_type]

    for field_name, field_spec in object_spec["properties"].items():
        try:
            field = {
                "name": field_name,
                "label": field_name.replace('_', ' ').capitalize(),
                "input_type": field_spec.get("input_type", "text"),
                "value": obj_properties.get(field_name, field_spec.get("default", "")),
                "options": field_spec.get("options", []),
                "editable": field_spec["editable"],
                "view": field_spec.get("view", "text"),
                "conditional_on": field_spec.get("conditional_on", None)
            }
            fields.append(field)
        except KeyError as e:
            print(f"Error in field specification for '{field_name}': missing key {e}")
        except Exception as e:
            print(f"Unexpected error in field specification for '{field_name}': {e}")

    return fields

# def generate_form(object_type, specifications, obj_properties):
#     fields = []
    
#     # Ensure the object_type exists in the specifications
#     if object_type not in specifications:
#         print(f"Error: '{object_type}' is not a valid object type in specifications.")
#         return fields
    
#     # Get the specific specifications for the given object_type
#     object_spec = specifications[object_type]
    
#     for field_name, field_spec in object_spec["properties"].items():
#         try:
#             field = {
#                 "name": field_name,
#                 "label": field_name.replace('_', ' ').capitalize(),
#                 "input_type": field_spec.get("input_type", "text"),
#                 "value": obj_properties.get(field_name, ""),
#                 "options": field_spec.get("options", []),
#                 "editable": field_spec["editable"],
#                 "view": field_spec.get("view", "text")
#             }
#             fields.append(field)
#         except KeyError as e:
#             print(f"Error in field specification for '{field_name}': missing key {e}")
#         except Exception as e:
#             print(f"Unexpected error in field specification for '{field_name}': {e}")
    
#     return fields

def validate_form_data(data, specifications):
    # The schema should be wrapped in a proper JSON schema format
    schema = {
        "type": "object",
        "properties": specifications["properties"],
        "required": [key for key, value in specifications["properties"].items() if value.get("required", False)]
    }
    validate(instance=data, schema=schema)

def handle_form_submission(form_data, object_type, db):
    try:
        # validate_form_data(form_data, object_specifications[object_type])
        if form_data.get("object_id"):
            db.update(form_data["object_id"], form_data)
        else:
            db.add(object_id=None, properties=form_data, object_type=object_type)
    except ValidationError as e:
        print("Form data validation failed:", e.message)
