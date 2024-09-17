from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from api import crud
from api.schemes.note import NoteCreate, NoteUpdate
from db.db import get_db


app = FastAPI()


@app.post("/notes/")
def create_note_endpoint(note: NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db=db, note=note)


@app.get("/notes")
def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_notes(db=db, skip=skip, limit=limit)


@app.get("/notes/{note_id}")
def read_note(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.get_note_by_id(db, note_id)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return db_note


@app.delete("/notes/{note_id}")
def delete_note_endpoint(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.delete_note(db=db, note_id=note_id)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"detail": "Note deleted successfully"}


@app.put("/notes/{note_id}")
def update_note_endpoint(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    db_note = crud.update_note(db=db, note_id=note_id, note=note)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return db_note
