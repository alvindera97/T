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

import os
import random
import unittest
from types import SimpleNamespace
from typing import List
from unittest.mock import patch

import eventlet
from confluent_kafka.admin import AdminClient
from faker import Faker
from fastapi import FastAPI
from pydantic import ValidationError

from json_defs.message import MessageJSON
from models import Chat
from tests.database import base
from user import User
from utils.functions import utility_functions as utils

faker = Faker()


class TestCreateMessageJSON(unittest.TestCase):
    """
    Test case class for tests on function for creating user message JSON object.
    Here, "User" may refer to user.User or any comparable user entity existing outside this code base.

    More importantly, the emphasis here is on the message from the user. This can be either generated from
    User.generate_message or received at the websocket (for example fastapi.Websocket.receive_json()
    """

    def test_function_returns_json_object_when_called_with_required_arguments(
        self,
    ) -> None:
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
        cls.user_generate_message_mock = patch(
            "utils.functions.utility_functions.User.generate_message",
            return_value="hello world",
        ).start()

    def test_function_takes_User_object_argument_where_the_passed_object_must_already_be_instantiated(
        self,
    ) -> None:
        """
        Test that the function takes User object argument which must have already been instantiated.
        :return: None
        """

        self.assertRaises(
            AssertionError, lambda: utils.generate_message_from_user(User, 0, 0, 0, 0)
        )
        try:
            utils.generate_message_from_user(self.user, 0, 0, 0, 0)
        except Exception:
            self.fail("Exception raised while generating message from User via utils.")

    def test_function_takes_other_other_arguments_including_instantiated_user_object_to_populate_return_value(
        self,
    ) -> None:
        """
        Test that function takes arguments as well as instantiated User object to populate return value.
        :return: None
        """
        self.assertRaises(
            AssertionError, lambda: utils.generate_message_from_user(User, 0, 0, 0, 0)
        )

        try:
            utils.generate_message_from_user(self.user, 0, 0, 0, 0)
        except Exception:
            self.fail("Exception raised while generating message from User via utils.")

    def test_function_calls_User_generate_message_method_once_during_function_call(
        self,
    ) -> None:
        """
        Test that User's generate_message method was called during execution of function as it is the function that
        generates the message content for the user.
        :return: None
        """
        utils.generate_message_from_user(self.user, 0, 0, 0, 0)

        self.user_generate_message_mock.assert_called_once_with("")

    def test_function_return_type_is_of_expected_json_type(self) -> None:
        """
        Test that the function returns a result of expected type.
        :return: None
        """
        self.assertTrue(
            isinstance(
                utils.generate_message_from_user(self.user, 0, 0, 0, 0), MessageJSON
            )
        )

    def test_function_returns_message_json_with_different_context_id_from_passed_context_id_if_parent_id_is_None(
        self,
    ) -> None:
        """
        Test that function returns message json with context_id different to that of passed context_id if parent_id is None.
        :return: None
        """
        context_id = 0
        message_json = utils.generate_message_from_user(self.user, 0, 0, 0)
        self.assertNotEqual(message_json.context_id, context_id)

    def test_function_returns_message_json_with_same_context_id_from_passed_context_id_if_parent_id_is_not_None(
        self,
    ) -> None:
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

    def test_function_takes_session_argument(self) -> None:
        """
        Test that function takes in session argument, this argument is used internally
        by the function to pick a database to operate on.
        :return: None
        """

        self.assertRaises(TypeError, lambda: utils.add_new_chat())

        try:
            utils.add_new_chat(self.session)
        except Exception as e:
            self.fail(f"Unexpected exception raised: {e}")

    def test_function_adds_new_chat_record_to_database(self) -> None:
        """
        Test that function adds new chat record to database.

        :return: None
        """

        count_before_addition = self.session.query(Chat).count()

        chat = utils.add_new_chat(self.session)

        self.assertEqual(self.session.query(Chat).first().uuid.__str__(), chat)
        self.assertEqual(self.session.query(Chat).count(), count_before_addition + 1)


class TestCreateApacheKafkaTopic(unittest.TestCase):
    """
    Test case class for tests on function for calling Apache Kafka topic.
    """

    @classmethod
    def setUpClass(cls):
        cls.confluent_kafka_admin_client = AdminClient(
            {"bootstrap.servers": "localhost:9092"}
        )
    @property
    def _current_kafka_test_topics(self) -> List[str]:
        """
        Get and return list of current kafka test topics.
        :return: List of kafka topics used for tests.
        """
        result = []
        topics: List[str] = (
            self.confluent_kafka_admin_client.list_topics().topics.keys()
        )
        for topic in topics:
            if topic.startswith("test_"):
                result.append(topic)

        return result

    @property
    def randomly_generated_kafka_test_topic(self) -> str:
        """
        Generate random kafka topic string
        :return: String topic name
        """
        topic = "test_" + faker.sentence().split(" ")[0].lower()
        current_topics = self._current_kafka_test_topics
        while topic in current_topics:
            topic = "test_" + faker.sentence().split(" ")[0].lower()

        return topic

    def test_function_takes_topic_argument(self) -> None:
        """
        Test that function takes 1 argument:
        1. topic name/title.
        :return: None
        """

        with self.assertRaises(TypeError) as context_1:
            utils.create_apache_kafka_topic(
                *(args := ["for"] + faker.sentence().split(" ") + ["extra", "measure"])
            )

        with self.assertRaises(TypeError) as context_2:
            utils.create_apache_kafka_topic()

        self.assertEqual(
            f"create_apache_kafka_topic() takes 1 positional argument but {len(args)} were given",
            context_1.exception.__str__(),
        )

        self.assertEqual(
            "create_apache_kafka_topic() missing 1 required positional argument: 'topic_title'",
            context_2.exception.__str__(),
        )

    def test_function_raises_value_error_on_invalid_inputs(self) -> None:
        """
        Test that function raises ValueError on invalid input for topic title and fastapi_application
        :return: None
        """
        topic = self.randomly_generated_kafka_test_topic

        with self.assertRaises(ValueError) as context_1:
            utils.create_apache_kafka_topic(1)

        with self.assertRaises(ValueError) as context_2:
            utils.create_apache_kafka_topic("")

        with self.assertRaises(ValueError) as context_3:
            utils.create_apache_kafka_topic(random.choice([True, False]))

        with self.assertRaises(ValueError) as context_4:
            utils.create_apache_kafka_topic("some topic")

        try:
            utils.create_apache_kafka_topic(topic)
        except RuntimeError as re:
            assert (
                re.__str__()
                == "fastapi_application instance has no running Apache Kafka Zookeeper server"
            )
        except Exception as e:
            self.fail(f"Unexpected exception raised: \n{e}")

        self.assertEqual(
            "create_apache_kafka_topic() 'topic_title' argument must be non-empty string!",
            context_1.exception.__str__(),
        )

        self.assertTrue(
            context_1.exception.__str__()
            == context_2.exception.__str__()
            == context_3.exception.__str__()
        )

        self.assertEqual(
            context_4.exception.__str__(),
            "create_apache_kafka_topic() 'topic_title' argument cannot contain spaces!",
        )

    def test_function_creates_kafka_topic(self) -> None:
        """
        Test function creates kafka topic with given name.
        :return: None
        """
        topic = self.randomly_generated_kafka_test_topic
        utils.create_apache_kafka_topic(topic)

        self.assertTrue(
            topic
            in AdminClient({"bootstrap.servers": "localhost:9092}"})
            .list_topics()
            .topics.keys()
        )

    def test_function_displays_warning_in_the_event_topic_to_be_created_already_exists(
        self,
    ) -> None:
        """
        Test function raises warning in the event that topic to be created has already been created.
        :return: None
        """
        topic = self.randomly_generated_kafka_test_topic

        with self.assertWarns(KafkaTopicAlreadyExists) as context:
            utils.create_apache_kafka_topic(topic)
            utils.create_apache_kafka_topic(topic)

        self.assertEqual(
            context.warning.__str__(),
            f'Kafka topic: "{topic}" already exists, thus not attempting creation.',
        )

    def test_function_raises_exception_if_kafka_topic_was_not_created_successfully(
        self,
    ) -> None:
        """
        Test function raises RuntimeError in the event that creation of kafka topic was not successful.
        :return: None
        """

        with self.assertRaises(RuntimeError) as contex:
            another_app = FastAPI()
            another_app.state.zookeeper_subprocess = object
            with patch(
                "select.select",
                return_value=(
                    [
                        SimpleNamespace(readline=lambda: "Some other value"),
                    ],
                    ["second"],
                    ["third"],
                ),
            ):
                wait_time = int(os.getenv("APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS"))
                utils.create_apache_kafka_topic("some_topic")

        self.assertEqual(
            contex.exception.__str__(),
            f"Failed to create kafka topic within {wait_time} second{'' if wait_time == 1 else 's'}. "
            f"To increase this wait time, increase APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS env.",
        )
