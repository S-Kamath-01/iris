# app/documents/service.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.documents import repository
from app.documents.schema import DocumentCreate, DocumentUpdate
from app.documents.model import Document


def create_document(db: Session, document: DocumentCreate) -> Document:
    return repository.create_document(db, document)


def get_document(db: Session, document_id: int) -> Document:
    db_document = repository.get_document(db, document_id)
    if db_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )
    return db_document


def get_documents(db: Session, skip: int = 0, limit: int = 20) -> list[Document]:
    return repository.get_documents(db, skip, limit)


def update_document(db: Session, document_id: int, document: DocumentUpdate) -> Document:
    db_document = repository.update_document(db, document_id, document)
    if db_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )
    return db_document


def delete_document(db: Session, document_id: int) -> None:
    deleted = repository.delete_document(db, document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )