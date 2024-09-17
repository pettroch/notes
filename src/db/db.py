from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost/notes"


engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()
engine.connect()

# Получение сессии бд
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
