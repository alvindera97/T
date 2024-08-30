"""
Base database test class module.

Classes:
  BaseTestDatabaseTestCase
"""
import os
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.testclient import TestClient

from api.endpoints import app
from database import db
from models.chat import Base


class BaseTestDatabaseTestCase(unittest.TestCase):
    """
    Base class for database test cases.
    """

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite:///:memory:",
            echo=os.getenv('DEBUG', False) == "True",
            connect_args={"check_same_thread": False}
        )
        cls.__session = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        Base.metadata.create_all(bind=cls.engine)

        cls.Session = cls.__session()

        # Override the `get_db` dependency in FastAPI
        def override_get_db():
            """
            Overrides the get_db function to use the in-memory SQLite database for testing.
            """
            DATABASE = cls.Session
            try:
                yield DATABASE
            finally:
                DATABASE.close()

        # Apply the override to the FastAPI app
        app.dependency_overrides[db.get_db] = override_get_db
        cls.client = TestClient(app)

    def setUp(self):
        self.session: Session = self.Session

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()
