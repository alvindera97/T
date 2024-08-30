"""
Base database test class module.

Classes:
  BaseTestDatabaseTestCase
"""
import inspect
import os
import unittest

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session
from starlette.testclient import TestClient

import models
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

        # Sanity check to ensure that all database tables are available before each test.
        for _, table in inspect.getmembers(models, inspect.isclass):
            try:
                self.session.query(table).count()
            except OperationalError:
                Base.metadata.create_all(bind=self.engine)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()
