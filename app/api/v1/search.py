# app/api/v1/search.py

from fastapi import APIRouter, Request

from app.search.search_engine import search as run_search
from app.search.schema import SearchResult, SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
def search(q: str, top_k: int, request: Request):
    context = request.app.state.search_context
    ranked_documents = run_search(query=q, context=context, top_k=top_k)

    results = [
        SearchResult(doc_id=doc.doc_id, score=doc.score)
        for doc in ranked_documents
    ]

    return SearchResponse(query=q, results=results)