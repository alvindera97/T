"""
Module for tests for application models.

Classes:
  ChatModelTestCase
"""

import inspect
import unittest
from uuid import uuid4

from sqlalchemy import String, Integer, UUID, ColumnDefault
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import DeclarativeMeta

import models


class ChatModelTestCase(unittest.TestCase):
    """
    Test case class for application Message model.
    """

    def test_model_is_a_class_model(self) -> None:
        """
        Test that the model is a class model
        :return: None
        """
        self.assertTrue(
            inspect.isclass(models.Chat),
            "The message model is supposed to be a class model.",
        )

    def test_model_inherits_from_sqlalchemy_base(self) -> None:
        """
        Test that the model inherits from sqlalchemy DeclarativeMeta.
        :return: None
        """

        # DeclarativeMeta in this instance will require some primary key and __tablename__

        self.assertTrue(
            models.Chat.uuid.primary_key,
            "uuid is supposed to be the primary key but it isn't the primary key!",
        )

        self.assertIsNotNone(models.Chat.__tablename__)
        self.assertEqual(models.Chat.__tablename__, "Chats")

        self.assertTrue(isinstance(models.Chat, DeclarativeMeta))

    def test_model_primary_key(self) -> None:
        """
        Test that the model has correct primary key
        :return: None
        """
        expected_primary_key = "uuid"
        primary_keys = [key.name for key in models.Chat.__table__.primary_key]
        self.assertEqual(
            len(primary_keys),
            1,
            f"There should be exactly one primary key!, Found: {len(primary_keys)}",
        )
        self.assertIn(
            expected_primary_key,
            primary_keys,
            f"Primary key, {expected_primary_key} isn't the primary key, the primary key is: {primary_keys[0]}",
        )

    def test_model_fields(self) -> None:
        """
        Test that the model has expected fields and expected properties defined on each field.
        """
        inspector = sqlalchemy_inspect(models.Chat)

        expected_fields = {
            "chat_title": {"type": String, "nullable": False, "default": None},
            "uuid": {
                "type": UUID,
                "nullable": False,
                "default": uuid4,
            },
            "chat_context": {"type": String, "nullable": False, "default": None},
            "chat_number_of_users": {"type": Integer, "nullable": False, "default": 1},
        }

        for field_name, attributes in expected_fields.items():
            with self.subTest(field=field_name):
                self.assertIn(
                    field_name, inspector.columns, f"Missing field: {field_name}"
                )

                column = inspector.columns[field_name]
                self.assertIsInstance(
                    column.type,
                    attributes["type"],
                    f"Field '{field_name}' is not of type {attributes['type']}.",
                )

                self.assertEqual(
                    column.nullable,
                    attributes["nullable"],
                    f"Field '{field_name}' nullable attribute is incorrect.",
                )

                if attributes["default"] is not None:
                    self.assertIsInstance(
                        column.default,
                        ColumnDefault,
                        f"Field '{field_name}' does not have a default value.",
                    )

                    if callable(attributes["default"]):
                        # We'll need to handle callables a bit differently
                        self.assertTrue(
                            callable(column.default.arg),
                            f"Field '{field_name}' default is not callable as expected.",
                        )
                        self.assertEqual(
                            column.default.arg.__name__,
                            attributes["default"].__name__,
                            f"Field '{field_name}' callable default function is incorrect.",
                        )
                    else:
                        self.assertEqual(
                            column.default.arg,
                            attributes["default"],
                            f"Field '{field_name}' default value is incorrect.",
                        )
                else:
                    self.assertIsNone(
                        column.default,
                        f"Field '{field_name}' should not have a default value.",
                    )
