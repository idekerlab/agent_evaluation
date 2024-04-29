from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.ae import load_tests, load_hypotheses

app = FastAPI()

# Get the absolute path to the project root directory
project_root = Path(__file__).resolve().parent.parent

# Mount the static directory using the absolute path
app.mount("/static", StaticFiles(directory=str(project_root / "static")), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home(request: Request):
    tests = ()
    return templates.TemplateResponse("home.html", {"request": request, "tests": tests})

@app.get("/test/{test_id}")
async def test_details(request: Request, test_id: str):
    test = load_tests(test_id)
    hypotheses = load_hypotheses(test_id)
    return templates.TemplateResponse("test_details.html", {"request": request, "test": test, "hypotheses": hypotheses})

# Run the app with: uvicorn app.main:app --reload