from sqlalchemy import Column, Integer, String, Text, DateTime, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.db import Base


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tags = Column(String(255), nullable=True)  # Можно использовать формат JSON для тегов
