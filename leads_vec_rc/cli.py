from fastapi import FastAPI

app = FastAPI(title="LEADS VeC Remote Controller")


@app.get("/")
async def index():
    return {"message": "Hello World"}
