# app/core/search_context.py

from dataclasses import dataclass
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.documents.model import Document
from app.indexing.model import Term, PostingRecord, IndexMetadata
from app.indexing.posting_list import Posting


@dataclass
class SearchContext:
    """In-memory search state, reconstructed from Postgres at startup."""

    inverted_index: Dict[str, List[Posting]]
    document_lengths: Dict[int, int]
    total_documents: int
    avg_doc_length: float

    @classmethod
    def build_from_db(cls, db: Session) -> "SearchContext":
        metadata = db.execute(
            select(IndexMetadata).where(IndexMetadata.id == 1)
        ).scalar_one()

        doc_rows = db.execute(select(Document.id, Document.token_count)).all()
        document_lengths = {doc_id: token_count for doc_id, token_count in doc_rows}

        posting_rows = db.execute(
            select(Term.text, PostingRecord.document_id, PostingRecord.term_freq)
            .join(PostingRecord, PostingRecord.term_id == Term.id)
        ).all()

        inverted_index: Dict[str, List[Posting]] = {}
        for term_text, document_id, term_freq in posting_rows:
            inverted_index.setdefault(term_text, []).append(
                Posting(doc_id=document_id, term_freq=term_freq)
            )

        return cls(
            inverted_index=inverted_index,
            document_lengths=document_lengths,
            total_documents=metadata.total_documents,
            avg_doc_length=metadata.avg_doc_length,
        )