"""
Module for tests on messages.

This module contains tests cases for messages and related functionality.

Classes:
  TestMessagesJSON
"""
import unittest
import random

from pydantic import ValidationError

from _json.message import MessageJSON


class TestMessagesJSON(unittest.TestCase):
    """
    Test case class for class defining messages JSON schema.
    """

    def test_message_json_schema(self) -> None:
        """
        Test message json instance is of valid schema
        :return: None
        """

        data = {
            "thread_id": 789,
            "context_id": 123,
            "partition_hint": 1,
            "content": "Hello, world!",
            "parent_message_id": random.choice([456, None]),
        }

        try:
            message = MessageJSON(**data)
        except ValidationError:
            self.fail("MessageJSON didn't return valid schema")

        self.assertEqual(message.content, data["content"])
        self.assertEqual(message.thread_id, data["thread_id"])
        self.assertEqual(message.context_id, data["context_id"])
        self.assertEqual(message.partition_hint, data["partition_hint"])
        self.assertEqual(message.parent_message_id, data["parent_message_id"])
