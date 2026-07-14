# scripts/ingest_documents.py

from sklearn.datasets import fetch_20newsgroups

from app.db.session import SessionLocal
from app.documents.model import Document

BATCH_SIZE = 1000


def ingest():
    print("Fetching 20 Newsgroups dataset...")
    data = fetch_20newsgroups(subset="all", remove=("headers", "footers", "quotes"))

    db = SessionLocal()
    try:
        batch = []
        for i, (text, target) in enumerate(zip(data.data, data.target)):
            category = data.target_names[target]
            doc = Document(category=category, title=None, content=text)
            batch.append(doc)

            if len(batch) >= BATCH_SIZE:
                db.bulk_save_objects(batch)
                db.commit()
                print(f"Inserted {i + 1} documents...")
                batch = []

        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            print(f"Inserted final batch. Total: {len(data.data)} documents.")
    finally:
        db.close()


if __name__ == "__main__":
    ingest()