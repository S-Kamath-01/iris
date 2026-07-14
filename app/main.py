# app/main.py

from fastapi import FastAPI

from app.core.config import settings
from app.api.v1 import documents

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(documents.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.APP_ENV}