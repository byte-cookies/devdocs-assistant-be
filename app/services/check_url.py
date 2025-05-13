# app/services/check_url.py

from typing import Optional
import httpx
from urllib.parse import urlparse
from urllib import robotparser


async def check_url_crawlable(url: str, client: Optional[httpx.AsyncClient] = None) -> dict:
    own_client = False
    try:
        # URL 유효성 검사
        if not url or url.startswith(("javascript:", "file:")):
            return {
                "url": url,
                "status_code": None,
                "crawlable": False,
                "isAccessible": False,
                "reason": "Invalid or unsupported URL scheme"
            }

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {
                "url": url,
                "status_code": None,
                "crawlable": False,
                "isAccessible": False,
                "reason": "URL must use http or https scheme"
            }

        if client is None:
            client = httpx.AsyncClient(timeout=10)
            own_client = True

        # POST 요청 → 실패 시 GET으로 fallback
        try:
            response = await client.post(url)
            if response.status_code == 405:
                response = await client.get(url)
        except httpx.HTTPError:
            response = await client.get(url)

        status_code = response.status_code

        # X-Robots-Tag 검사
        x_robots_tag = response.headers.get("X-Robots-Tag", "").lower()
        if any(tag in x_robots_tag for tag in ["noindex", "nofollow", "none"]):
            return {
                "url": url,
                "status_code": status_code,
                "crawlable": False,
                "isAccessible": False,
                "reason": f"Blocked by X-Robots-Tag: {x_robots_tag}"
            }

        if not (200 <= status_code < 400):
            return {
                "url": url,
                "status_code": status_code,
                "crawlable": False,
                "isAccessible": False,
                "reason": f"HTTP error with status code {status_code}"
            }

        # robots.txt 확인
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        robots_response = await client.get(robots_url)
        if robots_response.status_code == 404:
            can_fetch = True
            robots_reason = "robots.txt not found – assumed crawlable"
        else:
            rp = robotparser.RobotFileParser()
            rp.parse(robots_response.text.splitlines())
            can_fetch = rp.can_fetch("*", url)
            robots_reason = "Allowed by robots.txt" if can_fetch else "Disallowed by robots.txt"

        return {
            "url": url,
            "status_code": status_code,
            "crawlable": can_fetch,
            "isAccessible": can_fetch,
            "reason": robots_reason
        }

    except Exception as e:
        return {
            "url": url,
            "status_code": None,
            "crawlable": False,
            "isAccessible": False,
            "reason": f"Exception: {str(e)}"
        }
    finally:
        if own_client:
            await client.aclose()
