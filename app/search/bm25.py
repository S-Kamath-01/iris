# app/search/bm25.py

import math
from dataclasses import dataclass
from typing import Dict, List

def _score_term(
    f: int,
    df: int,
    doc_length: int,
    total_documents: int,
    avg_doc_length: float,
    k1: float,
    b: float,
) -> float:
    """
    BM25 contribution of a single term to a single document's score.
    Returns 0.0 if the term does not appear in this document (f == 0),
    since a term with zero frequency contributes nothing regardless of IDF.
    """
    if f == 0:
        return 0.0

    idf = math.log((total_documents - df + 0.5) / (df + 0.5) + 1)

    length_norm = 1 - b + b * (doc_length / avg_doc_length)
    tf_component = (f * (k1 + 1)) / (f + k1 * length_norm)

    return idf * tf_component


def score_document(
    term_freqs: dict[str, int],
    doc_freqs: dict[str, int],
    doc_length: int,
    total_documents: int,
    avg_doc_length: float,
    k1: float,
    b: float,
) -> float:
    """
    Full BM25 score for one document against a multi-term query.
    Sums each query term's contribution via _score_term.

    term_freqs: query term -> frequency of that term in this document (0 if absent)
    doc_freqs: query term -> number of documents in the corpus containing that term
    """
    total_score = 0.0
    for term, f in term_freqs.items():
        df = doc_freqs.get(term, 0)
        if df == 0:
            # Term never appears in the corpus at all (e.g. a typo query term) —
            # skip rather than risk a divide-by-zero-adjacent IDF blow-up.
            continue
        total_score += _score_term(f, df, doc_length, total_documents, avg_doc_length, k1, b)

    return total_score

@dataclass
class TermContribution:
    term: str
    contribution: float
    term_freq: int
    doc_freq: int


def explain_document_score(
    term_freqs: Dict[str, int],
    doc_freqs: Dict[str, int],
    doc_length: int,
    total_documents: int,
    avg_doc_length: float,
    k1: float,
    b: float,
) -> List[TermContribution]:
    return [
        TermContribution(
            term=term,
            contribution=_score_term(
                f=term_freqs[term],
                df=doc_freqs[term],
                doc_length=doc_length,
                total_documents=total_documents,
                avg_doc_length=avg_doc_length,
                k1=k1,
                b=b,
            ),
            term_freq=term_freqs[term],
            doc_freq=doc_freqs[term],
        )
        for term in term_freqs
    ]