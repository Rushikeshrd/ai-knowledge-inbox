from app.config import get_settings
from app.exceptions import ValidationAppError
from app.logging_config import get_logger, log_with_fields
from app.models import QueryResponse, SourceSnippet
from app.services.embeddings import embed_query
from app.services.llm import generate_answer
from app.services.vector_store import search_similar_chunks

logger = get_logger(__name__)

NO_CONTENT_ANSWER = "You haven't saved any content yet, so I have nothing to answer from. Add a note or URL first."


def answer_question(question: str, top_k: int) -> QueryResponse:
    if not question:
        raise ValidationAppError("'question' is required and cannot be empty.")

    settings = get_settings()
    effective_top_k = top_k or settings.top_k_default

    query_embedding = embed_query(question)
    matches = search_similar_chunks(query_embedding, effective_top_k)

    log_with_fields(
        logger, 20, "retrieval_completed", question_chars=len(question), matches=len(matches), top_k=effective_top_k
    )

    if not matches:
        return QueryResponse(answer=NO_CONTENT_ANSWER, sources=[], retrieved_chunk_count=0)

    context_snippets = [match["text"] for match in matches]
    answer = generate_answer(question, context_snippets)

    sources = [
        SourceSnippet(
            item_id=match["item_id"],
            title=match["title"],
            source_type=match["source_type"],
            source_url=match["source_url"],
            snippet=match["text"][:400],
            similarity=round(match["similarity"], 4),
        )
        for match in matches
    ]

    return QueryResponse(answer=answer, sources=sources, retrieved_chunk_count=len(matches))
