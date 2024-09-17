import uvicorn

from api.api import app
from db.db import Base, engine


if __name__ == "__main__":
    # Создание всех таблиц
    Base.metadata.create_all(bind=engine)

    uvicorn.run(app, host="localhost", port=80)
