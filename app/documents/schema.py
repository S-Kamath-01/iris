# app/documents/schema.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    category: str
    title: str | None = None
    content: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# add to app/documents/schema.py

class DocumentUpdate(BaseModel):
    category: str | None = None
    title: str | None = None
    content: str | None = None