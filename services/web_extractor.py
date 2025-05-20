import httpx
from bs4 import BeautifulSoup

async def extract_text_from_url(url: str) -> str:
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

    if main_content:
        return main_content.get_text(separator="\n", strip=True)

    return soup.get_text(separator="\n", strip=True)
