from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api import crud
from api.schemes.note import NoteCreate, NoteUpdate
from db.models.note import Note
from db.models.user import User
from db.db import get_db

from api.schemes.jwt import Token, TokenData
from api.schemes.user import UserCreate
from api.jwt.jwt import create_access_token, verify_token, decode_access_token


app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Проверка пароля 
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Хеширование пароля
def get_password_hash(password):
    return pwd_context.hash(password)

# Авторизован ли пользователь
def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    user = verify_token(token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return decode_access_token(token)


# Route выдачи токена
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Пытаемся получить текущего пользователя
    user = crud.get_user_by_username(db=db, username=form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"username": user.username, "id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


# Route регистрации пользователя
@app.post("/register")
def register_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    user = User(username=user.username, hashed_password=hashed_password)

    return crud.create_user(db=db, user=user)


# Route получения заметок (по дефолту 10 шт. Сделана пагинация)
@app.get("/notes")
def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    return crud.get_notes(db=db, skip=skip, limit=limit, user_id=current_user.id)


# Route создания заметки
@app.post("/notes")
def create_note_endpoint(note: NoteCreate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    return crud.create_note(db=db, note=note, user_id=current_user.id)


# Route поиска заметок по тегам
@app.get("/notes/search")
def search_notes_by_tags(tags: str, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    # Разделение строки тегов на список и удаление пустых значений
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # Ищем заметки, которые соответствуют хотя бы одному тегу и принадлежат текущему пользователю
    query = db.query(Note).filter(
        Note.user_id == current_user.id,  # Фильтрация по user_id текущего пользователя
        or_(
            *[Note.tags.ilike(f"%{tag}%") for tag in tags_list]
        )
    )
    
    return query.all()


# Route получения конкретной заметки по id
@app.get("/notes/{note_id}")
def read_note(note_id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    db_note = crud.get_note_by_id(db, note_id, user_id=current_user.id)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return db_note


# Route удаления конкретной заметки по id
@app.delete("/notes/{note_id}")
def delete_note_endpoint(note_id: int, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    db_note = crud.delete_note(db=db, note_id=note_id, user_id=current_user.id)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"detail": "Note deleted successfully"}


# Route обновления конкретной заметки по id
@app.put("/notes/{note_id}")
def update_note_endpoint(note_id: int, note: NoteUpdate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    db_note = crud.update_note(db=db, note_id=note_id, note=note, user_id=current_user.id)

    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return db_note
