from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class IngestRequest(BaseModel):
    source_type: Literal["note", "url"]
    text: str | None = Field(default=None, description="Required when source_type == 'note'")
    url: str | None = Field(default=None, description="Required when source_type == 'url'")

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @field_validator("url")
    @classmethod
    def strip_url(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class IngestResponse(BaseModel):
    id: int
    source_type: Literal["note", "url"]
    title: str
    chunk_count: int
    created_at: str


class ItemSummary(BaseModel):
    id: int
    source_type: Literal["note", "url"]
    title: str
    source_url: str | None
    preview: str
    chunk_count: int
    created_at: str


class ItemListResponse(BaseModel):
    items: list[ItemSummary]
    count: int


class QueryRequest(BaseModel):
    question: str
    top_k: int = Field(default=0, ge=0, le=20)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        return value.strip()


class SourceSnippet(BaseModel):
    item_id: int
    title: str
    source_type: Literal["note", "url"]
    source_url: str | None
    snippet: str
    similarity: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]
    retrieved_chunk_count: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
