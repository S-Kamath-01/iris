# app/indexing/model.py

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Term(Base):
    __tablename__ = "terms"

    id = Column(Integer, primary_key=True)
    text = Column(String(100), unique=True, nullable=False, index=True)

    postings = relationship("PostingRecord", back_populates="term")


class PostingRecord(Base):
    __tablename__ = "postings"

    id = Column(Integer, primary_key=True)
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    term_freq = Column(Integer, nullable=False)

    term = relationship("Term", back_populates="postings")

    __table_args__ = (
        UniqueConstraint("term_id", "document_id", name="uq_term_document"),
    )