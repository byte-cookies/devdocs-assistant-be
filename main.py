from fastapi import FastAPI
from routers import crawler, rag_router


app = FastAPI(title="WhyNot Squad API",)
app.include_router(crawler.router)
app.include_router(rag_router.router)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI!"}