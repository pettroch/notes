from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api import crud
from api.schemes.note import NoteCreate, NoteUpdate
from db.models.note import Note
from db.db import get_db


app = FastAPI()

# Route создания заметки
@app.post("/notes")
def create_note_endpoint(note: NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db=db, note=note)



# Route получения заметок (по дефолту 10 шт. Сделана пагинация)
@app.get("/notes")
def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_notes(db=db, skip=skip, limit=limit)


# Route поиска заметок по тегам
@app.get("/notes/search")
def search_notes_by_tags(tags: str, db: Session = Depends(get_db)):
    # Разделение строки тегов на список и удаление пустых значений
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Ищем хотя бы один подходящий тег
    query = db.query(Note).filter(
        or_(
            *[Note.tags.ilike(f"%{tag}%") for tag in tags_list]
        )
    )
    
    return query.all()


# Route получения конкретной заметки по id
@app.get("/notes/{note_id}")
def read_note(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.get_note_by_id(db, note_id)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return db_note


# Route удаления конкретной заметки по id
@app.delete("/notes/{note_id}")
def delete_note_endpoint(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.delete_note(db=db, note_id=note_id)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"detail": "Note deleted successfully"}


# Route обновления конкретной заметки по id
@app.put("/notes/{note_id}")
def update_note_endpoint(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    db_note = crud.update_note(db=db, note_id=note_id, note=note)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return db_note
