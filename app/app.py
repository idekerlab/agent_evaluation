# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import functools
from contextlib import asynccontextmanager
from app.sqlite_database import SqliteDatabase
from jsonschema import validate, ValidationError
from app.view_edit_specs import object_specifications
from app.config import load_database_uri
import csv
from io import StringIO
import os
import re
import json
from models.analysis_plan import AnalysisPlan
from models.review_plan import ReviewPlan
from services.analysisrunner import AnalysisRunner
from services.reviewrunner import ReviewRunner
from services.gene_validator import GeneValidator
import decimal
from decimal import Decimal, ROUND_HALF_UP
from models.judgment_space import JudgmentSpace
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import traceback
from models.json_object import Json


app = FastAPI()

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
# app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
app.mount("/static", StaticFiles(directory="react-app/build/static"), name="static")

templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# # Setup templates and static files
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

@app.get("/get_object_specs")
async def return_object_specs(request: Request):
    return object_specifications

@app.get("/objects/{object_type}")
async def list_objects(request: Request, object_type: str):
    if object_type not in object_specifications:
        raise HTTPException(status_code=404, detail="Object type not found")
    db = request.app.state.db
    objects = db.find(object_type)  # Fetch all objects of the given type
    if object_type == 'hypothesis':
        for index, obj in enumerate(objects):
            if ("agent_id" in obj['properties']):
                agent_id = obj['properties']['agent_id']
                agent_properties, agent_type = db.load(agent_id)
                if agent_properties:
                    objects[index]['properties']['agent_id'] = f"({agent_properties['name']}) {agent_id}"
            
            
    objects.reverse()
            
    return {"object_type": object_type, "objects": objects, "object_spec": object_specifications[object_type]}
    
    return templates.TemplateResponse("object_list.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "objects": objects})

# function to round up numeric values
def format_numeric_values(data):
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            # Check if the value is a numeric string, including negative numbers
            if value.lstrip('-').replace('.', '', 1).isdigit():
                try:
                    value_decimal = Decimal(value)
                    data[i][j] = str(value_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                except decimal.InvalidOperation:
                    continue
    return data

def preprocess_properties(properties, object_type):
    for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
        if prop_spec.get('type') == 'csv' and properties.get(prop_name):
            csv_data = StringIO(str(properties[prop_name]))
            reader = csv.reader(csv_data)
            rows = list(reader)

            # Format numeric values in CSV content, 2 decimal places
            formatted_rows = format_numeric_values(rows)
            properties[prop_name] = formatted_rows

    return properties

def handle_hypothesis(properties):
    hypo_text = properties["hypothesis_text"]
    file_path = "data/hgnc_genes.tsv"

    # Remove punctuation and parentheses, but keep hyphens
    cleaned_text = re.sub(r'[^\w\s-]', '', hypo_text)
    # Split into words
    words = re.split(r'\s+', cleaned_text)

    validator = GeneValidator(file_path)
    result = validator.validate_human_genes(words)
    
    properties['gene_symbols'] = result['official_genes']
    return properties

def generate_judgment_space_visualization(judgment_space):
    if not judgment_space.review_sets:
        return None, None

    try:
        judgment_space.generate_reviewer_judgment_dict()
        data = np.array(list(judgment_space.reviewer_judgment_dict.values()))
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(data, cmap='YlGnBu', cbar_kws={'label': 'Judgment Score'})
        plt.title('Reviewer Judgment Heatmap')
        plt.xlabel('Judgment Vector Index')
        plt.ylabel('Reviewer Index')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='svg')
        img_buffer.seek(0)
        svg_string = img_buffer.getvalue().decode()
        
        return svg_string, "image/svg+xml"
    except Exception as e:
        print(f"Error generating visualization: {str(e)}")
        return None, None

def process_object_links(db, properties, object_specifications, object_type):
    link_names = {}
    for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
        if prop_name not in ['object_id', 'created', 'name'] and prop_name in properties:
            if prop_spec['view'] == 'object_link':
                obj_id = properties[prop_name]
                link_names[obj_id] = get_link_name(db, obj_id)
            elif prop_spec['view'] == 'list_of_object_links':
                for obj_id in properties[prop_name]:
                    link_names[obj_id] = get_link_name(db, obj_id)
    return link_names

def get_link_name(db, obj_id):
    try:
        linked_object_properties, _ = db.load(obj_id)
        return linked_object_properties.get('name', 'unnamed') or 'unnamed'
    except Exception:
        return "Invalid ID"

@app.get("/objects/{object_type}/{object_id}")
async def view_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, object_type = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    
    processed_properties = preprocess_properties(properties, object_type)
    
    link_names = process_object_links(db, processed_properties, object_specifications, object_type)
    
    if object_type == "hypothesis":
        processed_properties = handle_hypothesis(processed_properties)
    
    visualizations = {}
    
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
                # Optionally, you can log the full traceback
                traceback.print_exc()
    
    return {
        "object_type": object_type, 
        "object": processed_properties,
        "object_spec": object_specifications[object_type],
        "link_names": link_names,
        "visualizations": visualizations
    }

# get the edit page with a new object of the same type and default properties
@app.get("/objects/{object_type}/blank/new")
async def new_object(request: Request, object_type: str):
    db = request.app.state.db
    default_properties = get_default_properties(object_type, object_specifications)
    new_object_id , new_properties, _ = db.add(object_id=None, properties=default_properties, object_type=object_type)
    new_properties["object_id"] = new_object_id
    new_properties["name"] = f"{object_type} {new_properties['created']}"
    form_fields = generate_form(db, object_type, object_specifications, new_properties)
    
    db.remove(new_object_id)
    
    return {"object_type": object_type, 
            "object": new_properties, 
            "form_fields": form_fields,
            "object_spec": object_specifications[object_type]}
    
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
@app.get("/objects/{object_type}/{object_id}/edit")
async def edit_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, _ = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    form_fields = generate_form(db, object_type, object_specifications, properties)
    
    return {"object_type": object_type, 
            "object": properties, 
            "form_fields": form_fields,
            "object_spec": object_specifications[object_type]}
    
    return templates.TemplateResponse("edit_object.html", {"request": request, 
                                                           "object_type": object_type, 
                                                           "object": properties, 
                                                           "form_fields": form_fields,
                                                           "object_spec": object_specifications[object_type]})

# get the edit page with a new object of the same type and same properties
@app.get("/objects/{object_type}/{object_id}/clone")
async def clone_object(request: Request, object_type: str, object_id: str):
    db = request.app.state.db
    properties, _ = db.load(object_id)
    if not properties:
        raise HTTPException(status_code=404, detail="Object not found")
    properties.pop('object_id', None)
    properties["name"] = f"{properties['name']} - Cloned"
    cloned_object_id, cloned_properties, _ = db.add(object_id=None, properties=properties, object_type=object_type)
    # cloned_properties["object_id"] = cloned_object_id
    # form_fields = generate_form(db, object_type, object_specifications, cloned_properties)
    
    return { "object_id": cloned_object_id}
    
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
                    field_obj_name = field_object['properties']['name'] if 'name' in field_object['properties'] else "unnamed"
                    field_obj_name = field_obj_name if len(field_obj_name) > 0 else "unnamed"
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
    # print(form_data)
    # Ensure the object_type exists in the specifications
    if object_type not in object_specifications:
        print(f"Error: '{object_type}' is not a valid object type in specifications.")
        return form_data

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
@app.post("/objects/{object_type}/{object_id}/new")
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
    
    default_properties = get_default_properties(object_type, object_specifications)
    new_object_id , new_properties, _ = db.add(object_id=None, properties=default_properties, object_type=object_type)
    form_data["object_id"] = new_object_id
    
    try:
        await handle_form_submission(form_data, object_type, db)
        object_id_from_form = form_data.get("object_id")
        return {"object_id": object_id_from_form}
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
    
@app.post("/objects/{object_type}/{object_id}/execute")
async def execute_object(request: Request, object_type: str, object_id: str):
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
        return {"url": f"/analysis_run/{analysis_run.object_id}"}
        return RedirectResponse(url=f"/objects/{object_type}/{analysis_run.object_id}", status_code=303)
    
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
        return {"url": f"/review_set/{review_set.object_id}"}
        return RedirectResponse(url=f"/objects/{object_type}/{review_set.object_id}", status_code=303)
  
@app.post("/objects/{object_type}/import")
async def import_object(request: Request, object_type: str):
    # You only get to *this* method from the ImportForm.js commponent
    # of the React app. To get to the ImportForm  requires
    # conditional handling in the ObjectList.js and App.js components!
    # So you must update those pages to allow any more types of
    # objects to be imported!
    form_data = await request.form()
    form_data = dict(form_data)
    
    db = request.app.state.db
    
    json_file = form_data.pop('json', None)
    if json_file:
        json_content = (await json_file.read()).decode('utf-8')
        json_obj = json.loads(json_content)
        # print("Import Content", json_obj)
        
        default_properties = get_default_properties(object_type, object_specifications)
        new_object_id , new_properties, _ = db.add(object_id=None, properties=default_properties, object_type=object_type)
        json_obj["object_id"] = new_object_id
        json_obj["data"] = convert_to_csv(json_obj['data'])
        
        try:
            await handle_form_submission(json_obj, object_type, db)
            return {"object_id": new_object_id}
        except FormSubmissionError as e:
            # Return an error response to the web app
            print("ERROR:", e)
            return HTMLResponse(content=f"<h1>Form Submission Error</h1><p>{e.message}</p>", status_code=400)
        except Exception as e:
            print("Exception:", e)
            # Return a generic error response
            return HTMLResponse(content="<h1>Unexpected Error</h1><p>Something went wrong.</p>", status_code=500)
        
    return {"error": "Something went wrong"}

def convert_to_csv(data):
    # Create a StringIO object to hold the CSV data as a string
    output = StringIO()

    csv_writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Write each row from the list of lists to the CSV
    for row in data:
        csv_writer.writerow(row)

    csv_content = output.getvalue()
    output.close()

    return csv_content
    
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_react_app(full_path: str, request: Request):
    # Serve the index.html file for any route that doesn't match an API endpoint
    index_file_path = os.path.join(os.getcwd(), "react-app", "build", "index.html")
    with open(index_file_path, "r") as file:
        return HTMLResponse(file.read())
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     object_types = list(object_specifications.keys())
#     return templates.TemplateResponse("home.html", {"request": request, "object_types": object_types})
        

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
            print("File:", csv_file)
            if (csv_file != "undefined"):
                if isinstance(csv_file, io.TextIOWrapper):
                    # This is the case when uploading a csv file into a dataset object
                    # Read the contents of the CSV file as text
                    csv_content = (await csv_file.read()).decode('utf-8')
                else:
                    # This is the case when importing a dataset object
                    csv_content = csv_file
                print("Content", csv_content)
                # # Include the CSV text data in form_data
                # form_data['data'] = csv_content
                # Process the CSV content
                csv_data = StringIO(csv_content)
                reader = csv.reader(csv_data)
                rows = list(reader)

                # Format numeric values in CSV content
                formatted_rows = format_numeric_values(rows)

                # Convert back to CSV string
                output = StringIO()
                writer = csv.writer(output)
                writer.writerows(formatted_rows)
                form_data['data'] = output.getvalue()
        
        if form_data.get("object_id"):
            db.update(form_data["object_id"], form_data)
        else:
            # db.add(object_id=None, properties=form_data, object_type=object_type)
            raise Exception("No object_id provided in form data")
    except ValidationError as e:
        raise FormSubmissionError(f"Form data validation failed: {e.message}")
    except Exception as e:
        raise FormSubmissionError(f"An error occurred while processing the form: {e}")


