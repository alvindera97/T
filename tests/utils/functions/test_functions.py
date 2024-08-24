"""
Module for tests on utility functions.

This module contains test cases for testing the functions module in the
utilities package and all related functionality to the
function module.

Classes:
  TestCreateMessageJSON
"""

import unittest

from pydantic import ValidationError

from utils.functions import utility_functions as utils


class TestCreateMessageJSON(unittest.TestCase):
    """
    Test case class for tests on function for creating user message JSON object.
    Here, "User" may refer to user.User or any comparable user entity existing outside this code base.

    More importantly, the emphasis here is on the message from the user. This can be either generated from
    User.generate_message or received at the websocket (for example fastapi.Websocket.receive_json()
    """

    def test_function_returns_json_object_when_called_with_required_arguments(self) -> None:
        """
        Test that return value of function is a JSON object.
        :return: None
        """
        try:
            utils.create_message_JSON("some message string", 0, 0, 0, 0)
        except ValidationError:
            self.fail("Function doesn't return result with expected schema.")
