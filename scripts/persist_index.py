# scripts/persist_index.py

from sqlalchemy import Integer, column, update, values
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.session import SessionLocal
from app.documents.model import Document
from app.indexing.model import IndexMetadata, SINGLETON_ID
from app.indexing.persistence import save_index_to_db
from scripts.build_index import build_index

BATCH_SIZE = 5000


def update_token_counts(db, index) -> None:
    rows = list(index.document_lengths.items())
    if not rows:
        return

    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start : start + BATCH_SIZE]
        token_counts = (
            values(
                column("id", Integer),
                column("token_count", Integer),
                name="token_counts",
            )
            .data(batch)
            .alias("token_counts")
        )

        stmt = (
            update(Document)
            .where(Document.id == token_counts.c.id)
            .values(token_count=token_counts.c.token_count)
        )
        db.execute(stmt)

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