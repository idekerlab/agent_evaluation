from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
# from jinja2 import Environment, FileSystemLoader
import csv
from io import StringIO
from app.ae import load_hypotheses
from app.database import Database
from app.view_edit_specs import object_specifications

print("object_specifications length:")
print(len(object_specifications))

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

@app.get("/")
async def home(request: Request):
    tests = db.query("match (n:test) RETURN n.id as id, n.created as created")
    return templates.TemplateResponse("home.html", {"request": request, "tests": tests})

@app.get("/test/{test_id}")
async def test_details(request: Request, test_id: str):
    hypotheses, test = load_hypotheses(db, test_id)
    return templates.TemplateResponse("test_details.html", {"request": request, "test": test, "hypotheses": hypotheses})

@app.get("/objects/{object_type}/{object_id}")
async def object_details(request: Request, object_type: str, object_id: str = None):
    if object_id:
        # Fetch the object from the database based on object_type and object_id
        result = db.query(f"MATCH (n:{object_type}) WHERE n.id = '{object_id}' RETURN n")
        object_data = result[0] if result else {}
    else:
        # Create a new empty object
        object_data = {}

    # Preprocess CSV data
    for prop_name, prop_spec in object_specifications[object_type]['properties'].items():
        if prop_spec.get('type') == 'csv' and object_data.get(prop_name):
            csv_data = StringIO(object_data[prop_name])
            reader = csv.reader(csv_data)
            object_data[prop_name] = list(reader)

    return templates.TemplateResponse("object_details.html", {
        "request": request,
        "object_type": object_type,
        "object_data": object_data,
        "object_spec": object_specifications[object_type]
    })

# Run the app with: uvicorn app.main:app --reload
