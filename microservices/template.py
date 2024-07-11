from fastapi import FastAPI, HTTPException, Request
import uvicorn

app = FastAPI()

# receive the form data and update the object, redirect to the view page
@app.post("/query")
async def perform_query(request: Request):
    form_data = await request.form()
    form_data = dict(form_data)

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
