from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.exceptions import UrlFetchError, ValidationAppError
from app.logging_config import get_logger, log_with_fields

logger = get_logger(__name__)

_ALLOWED_SCHEMES = {"http", "https"}


def validate_note_text(text: str | None) -> str:
    if not text:
        raise ValidationAppError("'text' is required and cannot be empty for source_type 'note'.")
    settings = get_settings()
    if len(text) > settings.max_note_chars:
        raise ValidationAppError(f"Note text exceeds max length of {settings.max_note_chars} characters.")
    return text


def _validate_url_format(url: str | None) -> str:
    if not url:
        raise ValidationAppError("'url' is required for source_type 'url'.")
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES or not parsed.netloc:
        raise ValidationAppError("'url' must be a valid absolute http(s) URL.")
    return url


def fetch_url_content(url: str) -> tuple[str, str]:
    """Fetch a URL and return (title, extracted_text). Raises UrlFetchError on failure."""
    validated_url = _validate_url_format(url)
    settings = get_settings()

    try:
        response = httpx.get(
            validated_url,
            timeout=settings.url_fetch_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "ai-knowledge-inbox/1.0"},
        )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise UrlFetchError(f"Timed out fetching URL after {settings.url_fetch_timeout_seconds}s.") from exc
    except httpx.HTTPStatusError as exc:
        raise UrlFetchError(f"URL returned HTTP {exc.response.status_code}.") from exc
    except httpx.RequestError as exc:
        raise UrlFetchError(f"Could not reach URL: {exc}") from exc

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type and "text" not in content_type:
        raise UrlFetchError(f"Unsupported content-type '{content_type}' for URL ingestion.")

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else validated_url
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)[: settings.max_fetched_page_chars]

    if not cleaned:
        raise UrlFetchError("No readable text content found at URL.")

    log_with_fields(logger, 20, "url_fetched", url=validated_url, extracted_chars=len(cleaned))
    return title, cleaned
