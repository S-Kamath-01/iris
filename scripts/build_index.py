# scripts/build_index.py

import time

from app.db.session import SessionLocal
from app.documents.model import Document
from app.indexing.inverted_index import InvertedIndex


def build_index() -> InvertedIndex:
    db = SessionLocal()
    index = InvertedIndex()

    try:
        start = time.time()

        documents = db.query(Document.id, Document.content).all()
        print(f"Fetched {len(documents)} documents from Postgres.")

        for doc_id, content in documents:
            index.add_document(doc_id, content)

        elapsed = time.time() - start

        total_postings = sum(len(postings) for postings in index.index.values())

        print(f"Indexed {index.doc_count} documents in {elapsed:.2f} seconds.")
        print(f"Vocabulary size: {index.vocabulary_size()} unique terms.")
        print(f"Total postings: {total_postings}")
        print(f"Avg postings per term: {total_postings / index.vocabulary_size():.2f}")

    finally:
        db.close()

    return index


if __name__ == "__main__":
    build_index()