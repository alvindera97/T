"""
Base database test class module.

Classes:
  BaseTestDatabaseTestCase
"""

import os
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
            echo=os.getenv("DEBUG", False) == "True",
            connect_args={"check_same_thread": False},
        )
        cls.connection = cls.engine.connect()
        cls.SessionFactory = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.connection
        )

        # Use the shared connection for the entire test lifecycle since we're using in-memory database for testing.
        cls.connection.begin()

        Base.metadata.create_all(bind=cls.connection)

        def override_get_db():
            session = cls.SessionFactory()
            try:
                yield session
            finally:
                session.rollback()
                session.close()

        app.dependency_overrides[db.get_db] = override_get_db
        cls.client = TestClient(app)

    def setUp(self):
        self.session = self.SessionFactory()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=cls.connection)
        cls.connection.close()
        cls.engine.dispose()
