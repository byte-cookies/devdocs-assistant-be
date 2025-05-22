from fastapi import APIRouter
from pydantic import BaseModel
from rag.rag_chain import run_rag_chain

router = APIRouter(prefix="/Langchain", tags=["langchain"])


class QueryRequest(BaseModel):
    query: str


@router.post("/rag/ask", summary="질문 응답 처리")
def ask_rag(req: QueryRequest):
    result = run_rag_chain(req.query)
    return result
