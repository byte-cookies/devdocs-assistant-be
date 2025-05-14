from fastapi import APIRouter, Query
from services.check_url import check_url_crawlable

router = APIRouter(prefix="/crawler", tags=["Crawler"])


@router.get("/check", summary="크롤링 가능 여부 확인")
async def check_crawlable(url: str = Query(..., description="확인할 대상 URL")):
    result = await check_url_crawlable(url)
    return result