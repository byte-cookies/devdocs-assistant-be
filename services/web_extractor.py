import httpx
from bs4 import BeautifulSoup
from services.dynamic_extractor import extract_dynamic_page_text

async def extract_text_from_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise ValueError(f"HTTP status {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")

        main_content = (
            soup.find("article") or
            soup.find("main") or
            soup.select_one("div#content, div.main, section.content")
        )

        text = main_content.get_text(separator="\n", strip=True) if main_content else soup.get_text(separator="\n", strip=True)

        if len(text.strip()) < 100:  # ✅ 동적 페이지 가능성 판단 기준
            raise ValueError("Too little content, fallback to dynamic extraction.")

        return text

    except Exception:
        # ✅ fallback: Playwright로 재시도
        return await extract_dynamic_page_text(url)
