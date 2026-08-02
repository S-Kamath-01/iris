# app/api/v1/search.py

import re

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.documents.model import Document
from app.auth.dependencies import get_current_user
from app.auth.model import User
from app.indexing.tokenizer import preprocess_text
from app.search.search_engine import (
    search as run_search,
    explain as explain_search,
    count_matching_documents,
)
from app.search.schema import SearchResult, SearchResponse, TermContributionResult

router = APIRouter(prefix="/search", tags=["search"])

PREVIEW_LENGTH = 250


def _build_preview(content: str, query: str, length: int = PREVIEW_LENGTH) -> str:
    normalized_content = " ".join(content.split())
    if not normalized_content:
        return ""

    lower_content = normalized_content.lower()
    query_terms = list(dict.fromkeys(re.findall(r"[a-z0-9]+", query.lower())))
    query_terms.extend(
        term for term in preprocess_text(query) if term not in query_terms
    )

    match_index = None
    match_length = 0
    for term in query_terms:
        index = lower_content.find(term)
        if index != -1 and (match_index is None or index < match_index):
            match_index = index
            match_length = len(term)

    if match_index is None:
        return normalized_content[:length].rstrip()

    half_window = length // 2
    start = max(0, match_index - half_window)
    end = min(len(normalized_content), match_index + match_length + half_window)
    snippet = normalized_content[start:end].strip()

    if start > 0:
        snippet = f"...{snippet}"
    if end < len(normalized_content):
        snippet = f"{snippet}..."
    return snippet


@router.get("/", response_model=SearchResponse)
def search(
    q: str,
    top_k: int,
    request: Request,
    explain: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    context = request.app.state.search_context
    ranked_documents = run_search(query=q, context=context, top_k=top_k)
    total_matches = count_matching_documents(query=q, context=context)

    doc_ids = [doc.doc_id for doc in ranked_documents]
    doc_rows = (
        db.query(Document.id, Document.category, Document.content)
        .filter(Document.id.in_(doc_ids))
        .all()
    )
    doc_metadata = {
        doc_id: (category, _build_preview(content, q))
        for doc_id, category, content in doc_rows
    }

    results = []
    for doc in ranked_documents:
        category, preview = doc_metadata.get(doc.doc_id, ("unknown", ""))
        explanation = None
        if explain:
            contributions = explain_search(query=q, doc_id=doc.doc_id, context=context)
            explanation = [
                TermContributionResult(
                    term=c.term, contribution=c.contribution,
                    term_freq=c.term_freq, doc_freq=c.doc_freq,
                )
                for c in contributions
            ]
        results.append(
            SearchResult(
                doc_id=doc.doc_id, score=doc.score,
                category=category, preview=preview,
                explanation=explanation,
            )
        )

    return SearchResponse(query=q, total_matches=total_matches, results=results)