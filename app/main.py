# app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import SessionLocal
from app.core.search_context import SearchContext
from app.api.v1 import documents, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        app.state.search_context = SearchContext.build_from_db(db)
    finally:
        db.close()
    yield



app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(documents.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.APP_ENV}