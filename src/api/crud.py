from sqlalchemy.orm import Session
from db.models.note import Note
from api.schemes.note import NoteCreate, NoteUpdate

# Создание заметки в бд
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

# Получение заметок из бд
def get_notes(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Note).offset(skip).limit(limit).all()

# Получение конкретной заметки из бд
def get_note_by_id(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

# Удаление заметки из бд (Плохой тон что-либо удалять из бд,
#                         лучше сделать флаг is_delete - true/false)
def delete_note(db: Session, note_id: int):
    db_note = get_note_by_id(db, note_id)
    if db_note:
        db.delete(db_note)
        db.commit()
    return db_note

# Обновление конкретной заметки (заголовок, контент, теги)
def update_note(db: Session, note_id: int, note: NoteUpdate):
    db_note = get_note_by_id(db, note_id)
    if db_note:
        db_note.title = note.title
        db_note.content = note.content
        db_note.tags = ",".join(note.tags)
        db.commit()
        db.refresh(db_note)
    return db_note
