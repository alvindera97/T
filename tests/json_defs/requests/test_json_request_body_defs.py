"""
Module for tests for api endpoints request json types
"""
import unittest

import pydantic

from json_defs import json


class TestSetUpChatRequestJsonProperties(unittest.TestCase):
    """
    Test class for testing chat set up request body properties.
    """

    def test_json_has_string_chat_context_field(self) -> None:
        """
        Test that json definition has required string chat context field.
        :return: None
        """
        self.assertTrue(issubclass(json.SetUpChatRequestBody, pydantic.BaseModel))
        self.assertEqual(json.SetUpChatRequestBody.model_fields.__len__(), 1)
        self.assertIsNotNone(json.SetUpChatRequestBody.model_fields.get("chat_context"))
        self.assertTrue(json.SetUpChatRequestBody.model_fields.get("chat_context").is_required())

        try:
            json.SetUpChatRequestBody(**{"chat_context": "some chat context"})
        except Exception as e:
            self.fail(f"Instantiation of object failed, exception: {e}")
