# app/search/schema.py

from pydantic import BaseModel


class TermContributionResult(BaseModel):
    term: str
    contribution: float
    term_freq: int
    doc_freq: int


class SearchResult(BaseModel):
    doc_id: int
    score: float
    explanation: list[TermContributionResult] | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]