from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
# from jinja2 import Environment, FileSystemLoader
import csv
from io import StringIO
from app.ae import load_hypotheses
from app.database import Database
from app.view_edit_specs import object_specifications, validate_object_specifications
from fastapi.exceptions import HTTPException

print("object_specifications length:")
print(len(object_specifications))
validate_object_specifications(object_specifications)

app = FastAPI()

# Get the absolute path to the project root directory
project_root = Path(__file__).resolve().parent.parent

# Mount the static directory using the absolute path
app.mount("/static", StaticFiles(directory=str(project_root / "static")), name="static")

templates = Jinja2Templates(directory="app/templates")

# Define the database connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "fredfred"

# Create the Neo4j database instance
db = Database(uri, user, password)

import csv
from io import StringIO

# def csv_to_table(csv_data):
#     csv_data = StringIO(csv_data)
#     reader = csv.reader(csv_data)
#     table = '<table>'
#     for row in reader:
#         table += '<tr>'
#         for cell in row:
#             table += f'<td>{cell}</td>'
#         table += '</tr>'
#     table += '</table>'
#     return table

# Create a custom Jinja2 environment
# jinja_env = Environment(loader=FileSystemLoader("app/templates"))
# jinja_env.filters['csvtable'] = csv_to_table

templates = Jinja2Templates(directory="app/templates")

# @app.get("/")
# async def home(request: Request):
#     tests = db.query("match (n:test) RETURN n.id as id, n.created as created")
#     return templates.TemplateResponse("home.html", {"request": request, "tests": tests})

@app.get("/")
async def home(request: Request):
    object_types = list(object_specifications.keys())
    return templates.TemplateResponse("home.html", {"request": request, "object_types": object_types})

@app.get("/test/{test_id}")
async def test_details(request: Request, test_id: str):
    hypotheses, test = load_hypotheses(db, test_id)
    return templates.TemplateResponse("test_details.html", {"request": request, "test": test, "hypotheses": hypotheses})

@app.get("/objects/{object_type}/{object_id}")
async def object_details(request: Request, object_type: str, object_id: str = None):
    if object_id:
        # Fetch the object from the database based on object_type and object_id
        result = db.query(f"MATCH (n:{object_type}) WHERE n.id = '{object_id}' RETURN n")
        if result:
            record = result[0]
            object_data = dict(record)
        else:
            object_data = {}    
    else:
        # Create a new empty object
        object_data = {}

    # Preprocess CSV data
    for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
        if prop_spec.get('type') == 'csv' and object_data.get(prop_name):
            csv_data = StringIO(object_data[prop_name])
            reader = csv.reader(csv_data)
            rows = list(reader)
            object_data[prop_name] = rows

    return templates.TemplateResponse("object_details.html", {
        "request": request,
        "object_type": object_type,
        "object_data": object_data,
        "object_spec": object_specifications[object_type]
    })

@app.get("/objects/{object_type}")
async def get_objects(object_type: str):
    # Fetch the list of objects from the database based on object_type
    objects = db.query(f"MATCH (n:{object_type}) RETURN n")
    return objects


@app.get("/objects/{object_type}/{object_id}/edit")
async def edit_object(request: Request, object_type: str, object_id: str):
    # Fetch the object from the database based on object_type and object_id
    #object_data = db.query(f"MATCH (n:{object_type}) WHERE n.id = '{object_id}' RETURN n")

    if object_id:
        # Fetch the object from the database based on object_type and object_id
        result = db.query(f"MATCH (n:{object_type}) WHERE n.id = '{object_id}' RETURN n")
        if result:
            record = result[0]
            object_data = dict(record)
        else:
            object_data = {}    
    else:
        raise HTTPException(status_code=404, detail="Object ID is required.")

    # Check if the object_data is None (i.e., the object was not found)
    if not object_data:
        # Return an error message to the user if the object is not found
        message = f"Sorry, object {object_id} was not found in the database."
        raise HTTPException(status_code=404, detail=message)


    return templates.TemplateResponse("object_details.html", {
        "request": request,
        "object_type": object_type,
        "object_data": object_data,
        "object_spec": object_specifications[object_type],
        "edit_mode": True
    })

@app.post("/objects/{object_type}/{object_id}/save")
async def save_object(request: Request, object_type: str, object_id: str):

    print("object_type:")
    print(object_type)  

    print("object_id:") 
    print(object_id)    

    # Get the edited data from the request body
    edited_data = await request.json()

    print("edited_data:")   
    print(edited_data)  

    # Update the object in the database with the edited data
    # ...

    # Return a success response
    return {"status": "success"}

# Run the app with: uvicorn app.main:app --reload
