from fastapi import FastAPI
from routers import crawler

app = FastAPI(title="Webcrawler API")
app.include_router(crawler.router)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI!"}