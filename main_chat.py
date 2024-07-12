import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.chat_app:app", host="127.0.0.1", port=8001, reload=True)