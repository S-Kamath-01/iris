# app/api/v1/documents.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.documents import service
from app.documents.schema import DocumentCreate, DocumentUpdate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    return service.create_document(db, document)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    return service.get_document(db, document_id)


@router.get("/", response_model=list[DocumentResponse])
def list_documents(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return service.get_documents(db, skip, limit)


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: int, document: DocumentUpdate, db: Session = Depends(get_db)):
    return service.update_document(db, document_id, document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    service.delete_document(db, document_id)