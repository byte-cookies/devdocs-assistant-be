from fastapi import APIRouter, Query
from pydantic import BaseModel
from services.check_url import check_url_crawlable
from services.web_extractor import extract_text_from_url
from services.embedder import embed_split_text, is_url_already_embedded
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

router = APIRouter(prefix="/crawler", tags=["Crawler"])

class URLRequest(BaseModel):
    url: str

@router.get("/check", summary="크롤링 가능 여부 확인")
async def check_crawlable(url: str = Query(..., description="확인할 대상 URL")):
    result = await check_url_crawlable(url)
    return result

@router.post("/ingest", summary="웹페이지 크롤링 + 분할 + 벡터 저장")
async def ingest_from_url(request: URLRequest):
    # 사전 중복 확인
    if is_url_already_embedded(request.url):
        return {
            "success": False,
            "message": "이미 저장된 URL입니다.",
            "source": request.url
        }
    # 크롤링 가능 여부 검사
    check = await check_url_crawlable(request.url)
    if not check["crawlable"]:
        return {
            "success": False,
            "message": f"크롤링 불가: {check['reason']}",
            "status_code": check["status_code"]
        }
    
    try:
        text = await extract_text_from_url(request.url)
        embed_split_text(text, request.url)

        return {
            "success": True,
            "message": "Document crawled, split and stored.",
            "source": request.url
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    
@router.get("/documents", summary="저장된 문서 내용 확인")
def list_documents(limit: int = Query(5, ge=1, le=100)):
    vectordb = Chroma(
        persist_directory="./vectorstore",
        embedding_function=OpenAIEmbeddings()
    )
    docs = vectordb.similarity_search("dummy", k=limit)

    results = []
    for doc in docs:
        results.append({
            "source": doc.metadata.get("source", "unknown"),
            "preview": doc.page_content[:300]  # 앞부분 300자만 표시
        })

    return {
        "count": len(results),
        "documents": results
    }