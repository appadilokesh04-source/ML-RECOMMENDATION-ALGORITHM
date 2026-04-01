import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # loads .env file
DATABASE_URL = os.getenv("DATABASE_URL")
# Engine = actual connection to MySQL
engine = create_engine(DATABASE_URL)

# SessionLocal = factory that creates DB sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
#
Base = declarative_base()# Base = parent class for all our ORM table models
def get_db():
    """
    FastAPI dependency — provides a DB session per request.
    Automatically closes session after request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()