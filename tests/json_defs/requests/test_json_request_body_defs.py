"""
Module for tests for api endpoints request json types
"""

import random
import unittest

import pydantic

from json_defs import json


class TestSetUpChatRequestJsonProperties(unittest.TestCase):
    """
    Test class for testing chat set up request body properties.
    """

    def test_json_has_expected_fields(self) -> None:
        """
        Test that json definition has expected fields.
        :return: None
        """
        self.assertTrue(issubclass(json.SetUpChatRequestBody, pydantic.BaseModel))
        self.assertEqual(json.SetUpChatRequestBody.model_fields.__len__(), 3)
        self.assertIsNotNone(json.SetUpChatRequestBody.model_fields.get("chat_title"))
        self.assertIsNotNone(json.SetUpChatRequestBody.model_fields.get("chat_context"))
        self.assertIsNotNone(
            json.SetUpChatRequestBody.model_fields.get("chat_number_of_users")
        )
        self.assertTrue(
            json.SetUpChatRequestBody.model_fields.get("chat_title").is_required()
        )
        self.assertTrue(
            json.SetUpChatRequestBody.model_fields.get("chat_context").is_required()
        )
        self.assertTrue(
            json.SetUpChatRequestBody.model_fields.get(
                "chat_number_of_users"
            ).is_required()
        )

        try:
            json.SetUpChatRequestBody(
                **{
                    "chat_title": "some chat title",
                    "chat_context": "some chat context",
                    "chat_number_of_users": random.randint(1, 1000),
                }
            )
        except Exception as e:
            self.fail(f"Instantiation of object failed, exception: {e}")

    def test_json_has_fields_of_expected_type(self) -> None:
        """
        Test that json definition has expected fields with expected types.
        """
        annotations = json.SetUpChatRequestBody.__annotations__
        self.assertEqual(annotations.get("chat_title"), str)
        self.assertEqual(annotations.get("chat_context"), str)
        self.assertEqual(annotations.get("chat_number_of_users"), int)
