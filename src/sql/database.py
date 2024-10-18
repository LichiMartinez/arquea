from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, dotenv_values
from contextlib import contextmanager

load_dotenv()
env = dotenv_values()

USER = env.get("POSTGRES_USER")
PASSWORD = env.get("POSTGRES_PASSWORD")
SERVER = env.get("POSTGRES_SERVER")
DATABASE = env.get("POSTGRES_DB")
SQLALCHEMY_DATABASE_URL = f'postgresql://{USER}:{PASSWORD}@{SERVER}/{DATABASE}'
breakpoint()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
