from fastapi import APIRouter

from app.models import QueryRequest, QueryResponse
from app.services.rag import answer_question

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    return answer_question(payload.question, payload.top_k)
