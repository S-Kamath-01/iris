# app/indexing/persistence.py

from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.indexing.inverted_index import InvertedIndex
from app.indexing.model import Term, PostingRecord

BATCH_SIZE = 5000


def save_index_to_db(db: Session, index: InvertedIndex) -> None:
    """
    Persist an in-memory InvertedIndex into the `terms` and `postings` tables.

    IMPORTANT: assumes both tables are currently empty. Running this against
    tables that already contain data will violate the unique constraints on
    Term.text and (term_id, document_id), and raise an IntegrityError.

    The entire operation is one transaction: batches are flushed (not committed)
    incrementally so later batches can reference earlier-inserted term_ids, but
    only one final commit() finalizes everything. Any failure triggers a full
    rollback, leaving the tables exactly as they were before the call.
    """
    try:
        # Step 1: bulk-insert all unique terms in one statement, using
        # RETURNING to get generated ids back without a separate re-query.
        term_texts = list(index.index.keys())
        stmt = insert(Term).returning(Term.id, Term.text)
        result = db.execute(stmt, [{"text": text} for text in term_texts])
        term_id_map = {text: term_id for term_id, text in result.all()}

        db.flush()

        # Step 2: build and insert PostingRecord rows in batches.
        batch: list[dict] = []
        for term_text, postings in index.index.items():
            term_id = term_id_map[term_text]
            for posting in postings:
                batch.append(
                    {
                        "term_id": term_id,
                        "document_id": posting.doc_id,
                        "term_freq": posting.term_freq,
                    }
                )
                if len(batch) >= BATCH_SIZE:
                    db.execute(insert(PostingRecord), batch)
                    db.flush()
                    batch = []

        if batch:
            db.execute(insert(PostingRecord), batch)
            db.flush()

        db.commit()

    except Exception:
        db.rollback()
        raise