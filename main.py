from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 추가
from routers import crawler, rag_router

app = FastAPI(
    title="Webcrawler API",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

# 👇 여기 CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:8000",  # 개발용
    "https://gukui.koreacentral.cloudapp.azure.com",  # 배포용
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crawler.router, prefix="/api")
app.include_router(rag_router.router, prefix="/api")

@app.get("/api")
def root():
    return {"message": "Hello from FastAPI!"}