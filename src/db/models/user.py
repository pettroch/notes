from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    telegram_id = Column(Integer, unique=True, nullable=True)
    notes = relationship("Note", back_populates="user")  # Определение связи с заметками
