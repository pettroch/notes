from pydantic import BaseModel
from typing import List, Optional


class NoteBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass
