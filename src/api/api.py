from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

from api.middleware import RateLimitMiddleware


templates = Jinja2Templates(directory="src/front/templates")

app = FastAPI()
app.add_middleware(RateLimitMiddleware, max_requests=10, period=60)
app.mount("/static", StaticFiles(directory="src/front"), name="static")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Проверка пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Хеширование пароля
def get_password_hash(password):
    return pwd_context.hash(password)


# Авторизован ли пользователь
def get_current_user(request: Request) -> TokenData:
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = verify_token(token)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return decode_access_token(token)


# Route выдачи токена
@app.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # Пытаемся получить текущего пользователя
    user = crud.get_user_by_username(db=db, username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"username": user.username, "id": user.id})

    response = RedirectResponse(url="/index", status_code=302)
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, max_age=3600
    )
    return response


# Route регистрации пользователя
@app.post("/register")
def register_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    user = User(username=user.username, hashed_password=hashed_password)

    return crud.create_user(db=db, user=user)


# Route получения заметок (по дефолту 10 шт. Сделана пагинация)
@app.get("/notes")
def read_notes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    return crud.get_notes(db=db, skip=skip, limit=limit, user_id=current_user.id)


# Route создания заметки
@app.post("/notes")
def create_note_endpoint(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    return crud.create_note(db=db, note=note, user_id=current_user.id)


# Route поиска заметок по тегам
@app.get("/notes/search")
def search_notes_by_tags(
    tags: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    # Разделение строки тегов на список и удаление пустых значений
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    # Ищем заметки, которые соответствуют хотя бы одному тегу и принадлежат текущему пользователю
    query = db.query(Note).filter(
        Note.user_id == current_user.id,  # Фильтрация по user_id текущего пользователя
        or_(*[Note.tags.ilike(f"%{tag}%") for tag in tags_list]),
    )

    return query.all()


# Route получения конкретной заметки по id
@app.get("/notes/{note_id}")
def read_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    db_note = crud.get_note_by_id(db, note_id, user_id=current_user.id)

    if db_note is None:
        return JSONResponse(status_code=404, content={"detail": "Заметка не найдена"})

    return db_note


# Route удаления конкретной заметки по id
@app.delete("/notes/{note_id}")
def delete_note_endpoint(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    db_note = crud.delete_note(db=db, note_id=note_id, user_id=current_user.id)

    if db_note is None:
        return JSONResponse(status_code=404, content={"detail": "Заметка не найдена"})

    return {"detail": "Note deleted successfully"}


# Route обновления конкретной заметки по id
@app.put("/notes/{note_id}")
def update_note_endpoint(
    note_id: int,
    note: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    db_note = crud.update_note(
        db=db, note_id=note_id, note=note, user_id=current_user.id
    )

    if db_note is None:
        return JSONResponse(status_code=404, content={"detail": "Заметка не найдена"})

    return db_note


# Route обработки Telegram-токена
@app.post("/telegram/auth")
async def telegram_auth(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    token = data.get("token")
    user_id = data.get("telegram_user_id")

    # Связываем Telegram аккаунт с существующим пользователем по токену
    user = crud.get_user_by_telegram_id(db, telegram_user_id=user_id)
    
    if not user:
        # Если пользователь не найден, создаем нового или выдаем ошибку
        return JSONResponse(status_code=404, content={"detail": "Пользователь не найден"})

    # Выдаем новый JWT токен для дальнейшей работы через веб-интерфейс
    access_token = create_access_token(data={"username": user.username, "id": user.id})
    
    return {"access_token": access_token}



# Страница авторизации
@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request, current_user: TokenData = Depends(get_current_user)):
    return templates.TemplateResponse("login.html", {"request": request})


# Страница создания заметки
@app.get("/create-note", response_class=HTMLResponse)
def get_create_note_page(request: Request, current_user: TokenData = Depends(get_current_user)):
    return templates.TemplateResponse("create-note.html", {"request": request})


# Страница получения заметок
@app.get("/get-notes", response_class=HTMLResponse)
def get_notes(request: Request, current_user: TokenData = Depends(get_current_user)):
    return templates.TemplateResponse("get-notes.html", {"request": request})


# Страница поиска заметок
@app.get("/search-notes", response_class=HTMLResponse)
def search_notes(request: Request, current_user: TokenData = Depends(get_current_user)):
    return templates.TemplateResponse("search-notes.html", {"request": request})


# Страница поиска заметки по ID
@app.get("/get-note", response_class=HTMLResponse)
def search_note_by_id(request: Request, current_user: TokenData = Depends(get_current_user)):
    return templates.TemplateResponse("search-note-by-id.html", {"request": request})


# Страница удаления заметки по ID
@app.get("/delete-note", response_class=HTMLResponse)
def delete_note_by_id(request: Request, current_user: TokenData = Depends(get_current_user)):
    return templates.TemplateResponse("delete-note-by-id.html", {"request": request})


# Страница обновления заметки по ID
@app.get("/update-note", response_class=HTMLResponse)
def delete_note_by_id(request: Request, current_user: TokenData = Depends(get_current_user)):
    return templates.TemplateResponse("update-note-by-id.html", {"request": request})


# Страница главного экрана
@app.get("/index", response_class=HTMLResponse)
def get_index_page(request: Request, current_user: TokenData = Depends(get_current_user)
):
    return templates.TemplateResponse("index.html", {"request": request})


# Маршрут для главной страницы
@app.get("/", response_class=HTMLResponse)
async def index_page(
    request: Request, current_user: TokenData = Depends(get_current_user)
):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": current_user}
    )




# Перенаправление на страницу входа, если пользователь не аутентифицирован
@app.middleware("http")
async def redirect_if_not_authenticated(request: Request, call_next):
    if request.url.path not in ["/login", "/token"] and not request.cookies.get(
        "access_token"
    ):
        return RedirectResponse(url="/login")
    response = await call_next(request)
    return response
