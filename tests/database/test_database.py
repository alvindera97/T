"""
Module for tests for application database

Classes:
  TestGetDB
"""

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from api.endpoints import app
from database import db
from models.chat import Base
from tests.database import base


class TestGetDB(base.BaseTestDatabaseTestCase):
    """
    Test case class for testing get_db function
    """

    def test_get_db_returns_session_object(self) -> None:
        """
        Test that get_db returns session object
        :return: None
        """

        override_get_db = app.dependency_overrides[db.get_db]
        db_generator = override_get_db()
        session = next(db_generator)

        self.assertTrue(isinstance(session, Session), f"The returned type is: {type(session)}")

        # Session needs to be properly closed.
        session.close()

    def test_get_db_returns_session_object_without_any_missing_tables(self) -> None:
        """
        Test that get_db returns session of database without any missing tables
        :return: None
        """
        overridden_get_db = app.dependency_overrides[db.get_db]
        db_generator = overridden_get_db()
        session: Session = next(db_generator)

        inspector = inspect(session.get_bind())
        existing_tables_in_db_returned_db_session = inspector.get_table_names()

        all_db_tables = Base.metadata.tables.keys()

        self.assertEqual(0,  # alembic_version table is not created in test database
                         len(set(existing_tables_in_db_returned_db_session).difference({'alembic_version'}).difference(
                             set(all_db_tables))))
