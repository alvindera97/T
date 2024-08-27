"""
Module for tests for application models.

Classes:
  ChatModelTestCase
"""
import inspect
import unittest

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
        self.assertTrue(inspect.isclass(models.Chat), "The message model is supposed to be a class model.")

    def test_model_inherits_from_sqlalchemy_base(self) -> None:
        """
        Test that the model inherits from sqlalchemy DeclarativeMeta.
        :return: None
        """

        # DeclarativeMeta in this instance will require some primary key and __tablename__

        self.assertTrue(models.Chat.uuid.primary_key, "uuid is supposed to be the primary key but it isn't the primary key!")

        self.assertIsNotNone(models.Chat.__tablename__)
        self.assertEqual(models.Chat.__tablename__, "Chats")

        self.assertTrue(isinstance(models.Chat, DeclarativeMeta))

    def test_model_has_chat_uuid_column(self) -> None:
        """
        Test that the model has a chat uuid column.
        :return: None
        """
        self.assertIsNotNone(models.Chat.uuid)
