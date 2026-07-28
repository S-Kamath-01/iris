# app/search/schema.py

from pydantic import BaseModel


class SearchResult(BaseModel):
    doc_id: int
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]