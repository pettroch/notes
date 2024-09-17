import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from api import crud
from api.schemes.note import NoteCreate, NoteUpdate
from db.db import get_db


app = FastAPI()


@app.post("/notes/")
def create_note_endpoint(note: NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db=db, note=note)
