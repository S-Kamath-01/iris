# scripts/persist_index.py

from app.db.session import SessionLocal
from app.indexing.persistence import save_index_to_db
from scripts.build_index import build_index


def main():
    index = build_index()

    db = SessionLocal()
    try:
        print("Persisting index to Postgres...")
        save_index_to_db(db, index)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()