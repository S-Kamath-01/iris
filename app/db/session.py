# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# The engine manages the connection pool to Postgres.
engine = create_engine(settings.DATABASE_URL)

# SessionLocal is a *factory* — calling SessionLocal() creates a new Session
# bound to a connection borrowed from the engine's pool.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency: yields a DB session for the duration of one request,
    and guarantees it's closed afterward (even if the request raised an error).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()