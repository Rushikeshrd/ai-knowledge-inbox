from fastapi import APIRouter

from app.db import get_connection
from app.exceptions import ValidationAppError
from app.logging_config import get_logger, log_with_fields
from app.models import IngestRequest, IngestResponse, ItemListResponse, ItemSummary
from app.services import items_repository
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts
from app.services.ingestion import fetch_url_content, validate_note_text
from app.services.vector_store import insert_chunks

router = APIRouter(tags=["items"])
logger = get_logger(__name__)

PREVIEW_LENGTH = 200


@router.post("/ingest", response_model=IngestResponse, status_code=201)
def ingest_item(payload: IngestRequest) -> IngestResponse:
    if payload.source_type == "note":
        text = validate_note_text(payload.text)
        title = text[:60] + ("..." if len(text) > 60 else "")
        source_url = None
        raw_content = text
    elif payload.source_type == "url":
        if not payload.url:
            raise ValidationAppError("'url' is required for source_type 'url'.")
        title, raw_content = fetch_url_content(payload.url)
        source_url = payload.url
    else:  # pragma: no cover - guarded by pydantic Literal already
        raise ValidationAppError("Unsupported source_type.")

    chunks = chunk_text(raw_content)
    if not chunks:
        raise ValidationAppError("No content could be extracted to chunk and index.")

    embeddings = embed_texts(chunks)

    with get_connection() as conn:
        item_row = items_repository.create_item(conn, payload.source_type, title, raw_content, source_url)
        chunk_count = insert_chunks(conn, item_row["id"], chunks, embeddings)
        conn.commit()

    log_with_fields(
        logger, 20, "item_ingested",
        item_id=item_row["id"], source_type=payload.source_type, chunk_count=chunk_count,
    )

    return IngestResponse(
        id=item_row["id"],
        source_type=payload.source_type,
        title=title,
        chunk_count=chunk_count,
        created_at=item_row["created_at"],
    )


@router.get("/items", response_model=ItemListResponse)
def list_items() -> ItemListResponse:
    rows = items_repository.list_items()
    items = [
        ItemSummary(
            id=row["id"],
            source_type=row["source_type"],
            title=row["title"],
            source_url=row["source_url"],
            preview=row["raw_content"][:PREVIEW_LENGTH],
            chunk_count=row["chunk_count"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
    return ItemListResponse(items=items, count=len(items))
