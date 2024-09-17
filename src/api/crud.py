from sqlalchemy.orm import Session
from db.models.note import Note
from api.schemes.note import NoteCreate, NoteUpdate


def create_note(db: Session, note: NoteCreate):
    db_note = Note(
        title=note.title,
        content=note.content,
        tags=", ".join(note.tags)  # Сохраняем теги как строку
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note