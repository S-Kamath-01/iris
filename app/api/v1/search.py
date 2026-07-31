# app/api/v1/search.py

from fastapi import APIRouter, Request

from app.search.search_engine import search as run_search
from app.search.schema import SearchResult, SearchResponse
from app.search.search_engine import search as run_search, explain as explain_search
from app.search.schema import SearchResult, SearchResponse, TermContributionResult
router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
def search(q: str, top_k: int, request: Request, explain: bool = False):
    context = request.app.state.search_context
    ranked_documents = run_search(query=q, context=context, top_k=top_k)

    results = []
    for doc in ranked_documents:
        explanation = None
        if explain:
            contributions = explain_search(query=q, doc_id=doc.doc_id, context=context)
            explanation = [
                TermContributionResult(
                    term=c.term,
                    contribution=c.contribution,
                    term_freq=c.term_freq,
                    doc_freq=c.doc_freq,
                )
                for c in contributions
            ]
        results.append(SearchResult(doc_id=doc.doc_id, score=doc.score, explanation=explanation))

    return SearchResponse(query=q, results=results)