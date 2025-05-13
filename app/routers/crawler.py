from fastapi import APIRouter, Query
from app.services.check_url import check_url_crawlable

router = APIRouter(prefix="/crawler", tags=["Crawler"])


@router.api_route("/check", methods=["GET", "POST"])
async def check_crawlable(url: str = Query(..., description="확인할 대상 URL")):
    result = await check_url_crawlable(url)
    return result