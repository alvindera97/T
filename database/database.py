import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from models.chat import Base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(SessionLocal)  # ensure thread-safety


def init_db():
    """
    Initialise the database and fill in any missing tables.
    :return: None
    """
    model_tables = Base.metadata.tables.keys()

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    missing_tables = set(model_tables) - set(existing_tables)

    if missing_tables:
        Base.metadata.create_all(bind=engine)


def get_db():
    """
    Provides a session object to the API endpoints.
    This session is tied to the current request context.
    """
    init_db()
    db: Session = session()
    try:
        return db
    finally:
        db.close()
