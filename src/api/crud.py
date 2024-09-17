from sqlalchemy.orm import Session
from db.models.note import Note
from db.models.user import User
from api.schemes.note import NoteCreate, NoteUpdate
from api.schemes.user import UserCreate


# Создание пользователя в бд
def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        hashed_password=user.hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# Получить юзера из бд
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# Создание заметки в бд
def create_note(db: Session, note: NoteCreate, user_id: int):
    db_note = Note(
        title=note.title,
        content=note.content,
        tags=",".join(note.tags),  # Сохраняем теги как строку
        user_id=user_id
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note


# Получение заметок из бд
def get_notes(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(Note).filter(Note.user_id == user_id).offset(skip).limit(limit).all()


# Получение конкретной заметки из бд
def get_note_by_id(db: Session, note_id: int, user_id: int):
    return db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()



# Удаление заметки из бд (Плохой тон что-либо удалять из бд,
#                         лучше сделать флаг is_delete - true/false)
def delete_note(db: Session, note_id: int, user_id: int):
    db_note = get_note_by_id(db, note_id, user_id)
    
    if db_note:
        db.delete(db_note)
        db.commit()

    return db_note



# Обновление конкретной заметки (заголовок, контент, теги)
def update_note(db: Session, note_id: int, note: NoteUpdate, user_id: int):
    db_note = get_note_by_id(db, note_id, user_id)
    
    if db_note:
        if note.title is not None:
            db_note.title = note.title

        if note.content is not None:
            db_note.content = note.content

        if note.tags is not None:
            db_note.tags = ",".join(note.tags)

        db.commit()
        db.refresh(db_note)
    
    return db_note
