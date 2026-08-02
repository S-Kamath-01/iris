# app/search/search_engine.py

import heapq
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from app.core.config import settings
from app.core.search_context import SearchContext
from app.indexing.tokenizer import preprocess_text
from app.search.bm25 import score_document, explain_document_score, TermContribution


@dataclass
class RankedDocument:
    doc_id: int
    score: float


def search(query: str, context: SearchContext, top_k: int = 10) -> List[RankedDocument]:
    query_terms = list(dict.fromkeys(preprocess_text(query)))

    doc_freqs: Dict[str, int] = {}
    term_freqs_per_doc: Dict[int, Dict[str, int]] = defaultdict(dict)

    for term in query_terms:
        postings = context.inverted_index.get(term, [])
        doc_freqs[term] = len(postings)
        for posting in postings:
            term_freqs_per_doc[posting.doc_id][term] = posting.term_freq

    scored_candidates = [
        RankedDocument(
            doc_id=doc_id,
            score=score_document(
                term_freqs=term_freqs,
                doc_freqs=doc_freqs,
                doc_length=context.document_lengths[doc_id],
                total_documents=context.total_documents,
                avg_doc_length=context.avg_doc_length,
                k1=settings.BM25_K1,
                b=settings.BM25_B,
            ),
        )
        for doc_id, term_freqs in term_freqs_per_doc.items()
    ]

    return heapq.nlargest(top_k, scored_candidates, key=lambda doc: doc.score)

def count_matching_documents(query: str, context: SearchContext) -> int:
    """Size of the union candidate set — same union logic as search(), without scoring/top-k."""
    query_terms = list(dict.fromkeys(preprocess_text(query)))
    matching_doc_ids = set()
    for term in query_terms:
        for posting in context.inverted_index.get(term, []):
            matching_doc_ids.add(posting.doc_id)
    return len(matching_doc_ids)

def explain(query: str, doc_id: int, context: SearchContext) -> List[TermContribution]:
    query_terms = list(dict.fromkeys(preprocess_text(query)))

    term_freqs: Dict[str, int] = {}
    doc_freqs: Dict[str, int] = {}

    for term in query_terms:
        postings = context.inverted_index.get(term, [])
        doc_freqs[term] = len(postings)
        for posting in postings:
            if posting.doc_id == doc_id:
                term_freqs[term] = posting.term_freq

    return explain_document_score(
        term_freqs=term_freqs,
        doc_freqs=doc_freqs,
        doc_length=context.document_lengths[doc_id],
        total_documents=context.total_documents,
        avg_doc_length=context.avg_doc_length,
        k1=settings.BM25_K1,
        b=settings.BM25_B,
    )