# scripts/persist_index.py

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.session import SessionLocal
from app.documents.model import Document
from app.indexing.model import IndexMetadata, SINGLETON_ID
from app.indexing.persistence import save_index_to_db
from scripts.build_index import build_index


def update_token_counts(db, index) -> None:
    mappings = [
        {"id": doc_id, "token_count": length}
        for doc_id, length in index.document_lengths.items()
    ]
    db.bulk_update_mappings(Document, mappings)
    db.commit()


def upsert_index_metadata(db, index) -> None:
    stmt = pg_insert(IndexMetadata).values(
        id=SINGLETON_ID,
        total_documents=index.doc_count,
        avg_doc_length=index.average_document_length(),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "total_documents": stmt.excluded.total_documents,
            "avg_doc_length": stmt.excluded.avg_doc_length,
        },
    )
    db.execute(stmt)
    db.commit()


def main():
    index = build_index()

    db = SessionLocal()
    try:
        print("Persisting index to Postgres...")
        save_index_to_db(db, index)

        print("Updating document token counts...")
        update_token_counts(db, index)

        print("Upserting index metadata...")
        upsert_index_metadata(db, index)

        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()