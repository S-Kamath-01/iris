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
    category: str
    preview: str
    explanation: list[TermContributionResult] | None = None


class SearchResponse(BaseModel):
    query: str
    total_matches: int
    results: list[SearchResult]