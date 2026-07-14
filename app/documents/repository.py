# app/documents/repository.py

from sqlalchemy.orm import Session

from app.documents.model import Document
from app.documents.schema import DocumentCreate, DocumentUpdate


def create_document(db: Session, document: DocumentCreate) -> Document:
    db_document = Document(**document.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()


def get_documents(db: Session, skip: int = 0, limit: int = 20) -> list[Document]:
    return db.query(Document).offset(skip).limit(limit).all()


def delete_document(db: Session, document_id: int) -> bool:
    db_document = get_document(db, document_id)
    if db_document is None:
        return False
    db.delete(db_document)
    db.commit()
    return True

def update_document(db: Session, document_id: int, document: DocumentUpdate) -> Document | None:
    db_document = get_document(db, document_id)
    if db_document is None:
        return None
    for key, value in document.model_dump(exclude_unset=True).items():
        setattr(db_document, key, value)
    db.commit()
    db.refresh(db_document)
    return db_document