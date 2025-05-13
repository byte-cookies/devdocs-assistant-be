from fastapi import FastAPI
from app.routers import crawler

app = FastAPI(title="Webcrawler API")
app.include_router(crawler.router)