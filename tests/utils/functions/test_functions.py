"""
Module for tests on utility functions.

This module contains test cases for testing the functions module in the
utilities package and all related functionality to the
function module.

Classes:
  TestCreateMessageJSON
  TestGenerateMessage
  TestAddChat
"""

import unittest
from unittest.mock import patch

from pydantic import ValidationError

from json_defs.message import MessageJSON
from models import Chat
from tests.database import base
from user import User
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


class TestGenerateMessage(unittest.TestCase):
    """
    Test case class for tests on function for generating message.
    """

    @classmethod
    def setUpClass(cls):
        cls.user = User("some name", "some url")

    def test_function_takes_User_object_argument_where_the_passed_object_must_already_be_instantiated(self) -> None:
        """
        Test that the function takes User object argument which must have already been instantiated.
        :return: None
        """

        self.assertRaises(AssertionError, lambda: utils.generate_message_from_user(User, 0, 0, 0, 0))
        try:
            utils.generate_message_from_user(self.user, 0, 0, 0, 0)
        except Exception:
            self.fail("Exception raised while generating message from User via utils.")

    def test_function_takes_other_other_arguments_including_instantiated_user_object_to_populate_return_value(
            self) -> None:
        """
        Test that function takes arguments as well as instantiated User object to populate return value.
        :return: None
        """
        self.assertRaises(AssertionError, lambda: utils.generate_message_from_user(User, 0, 0, 0, 0))

        try:
            utils.generate_message_from_user(self.user, 0, 0, 0, 0)
        except Exception:
            self.fail("Exception raised while generating message from User via utils.")

    @patch("user.User.generate_message", return_value="hello world")
    def test_function_calls_User_generate_message_method_once_during_function_call(self,
                                                                                   user_generate_message_mock) -> None:
        """
        Test that User's generate_message method was called during execution of function as it is the function that
        generates the message content for the user.
        :return: None
        """
        utils.generate_message_from_user(self.user, 0, 0, 0, 0)

        user_generate_message_mock.assert_called_once_with("")

    @patch("user.User.generate_message", return_value="hello world")
    def test_function_return_type_is_of_expected_json_type(self, *_) -> None:
        """
        Test that the function returns a result of expected type.
        :return: None
        """
        self.assertTrue(isinstance(utils.generate_message_from_user(self.user, 0, 0, 0, 0), MessageJSON))

    @patch("user.User.generate_message", return_value="hello world")
    def test_function_returns_message_json_with_different_context_id_from_passed_context_id_if_parent_id_is_None(
            self, *_) -> None:
        """
        Test that function returns message json with context_id different to that of passed context_id if parent_id is None.
        :return: None
        """
        context_id = 0
        message_json = utils.generate_message_from_user(self.user, 0, 0, 0)
        self.assertNotEqual(message_json.context_id, context_id)

    @patch("user.User.generate_message", return_value="hello world")
    def test_function_returns_message_json_with_same_context_id_from_passed_context_id_if_parent_id_is_not_None(
            self, *_) -> None:
        """
        Test that function returns message json with same context_id as passed context_id if parent_id is not None
        :return: None
        """
        context_id = 0
        message_json = utils.generate_message_from_user(self.user, 0, 0, 0, context_id)
        self.assertEqual(message_json.context_id, context_id)


class TestAddChat(base.BaseTestDatabaseTestCase):
    """
    Test case class for tests on function for adding Chat to database
    """

    def test_function_adds_new_chat_record_to_database(self) -> None:
        """
        Test that function adds new chat record to database.

        :return: None
        """

        count_before_addition = self.session.query(Chat).count()

        chat = utils.add_new_chat()

        self.assertEqual(self.session.query(Chat).first().uuid.__str__(), chat)
        self.assertEqual(self.session.query(Chat).count(), count_before_addition + 1)
