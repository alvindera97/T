"""
Module for tests on user / client.

This module contains test cases for testing the "User" (otherwise called Client) entity
and all related functionality.

Classes:
  TestUserTestCase
  TestUserAsyncioMethodsTestCase
"""

import inspect
import unittest
from collections import Counter
from types import SimpleNamespace
from unittest.mock import patch

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from faker import Faker

from role import Role
from user import User
from utils.exceptions import OperationNotAllowedException


class TestUserTestCase(unittest.TestCase):
    """
    Test case class for tests for User entity
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Defines attributes and calls for test case, before tests are executed.
        :return: None
        """
        super().setUpClass()
        cls.user = User()

    def setUp(self) -> None:
        """
        Method defining what must be run before each test method within this class.
        :return: None
        """
        super().setUp()

    def tearDown(self) -> None:
        """
        Method defining actions after each test method within this class.
        :return: None
        """
        super().tearDown()
        self.user.role = Role.NOT_SET

    def test_user_class_exists(self) -> None:
        """
        Tests if User class exists
        :return: None
        """
        self.assertTrue(inspect.isclass(User))

    def test_user_has_role_attribute(self) -> None:
        """
        Test that initialized user object has role attribute.

        :return: None
        """
        self.assertTrue(hasattr(User, "role"))

    def test_user_has_name_attribute(self) -> None:
        """
        Test that initialized user object has name attribute
        :return: None
        """
        self.assertTrue(hasattr(User(), "name"))

    def test_user_has_display_picture_attribute(self) -> None:
        """
        Test that user object has display picture attribute
        :return: None
        """
        self.assertTrue(hasattr(User(), "display_picture_url"))

    def test_that_user_object_by_default_has_empty_username_and_image_url(self):
        """
        Test that at initialisation of User object, if user name and or display picture is not supplied
        as arguments to the constructor, name and display_picture_url attributes default to empty string.
        :return: None
        """
        self.assertEqual(self.user.name, "")
        self.assertEqual(self.user.display_picture_url, "")

    def test_that_passed_name_and_display_picture_url_are_applied_to_user_instance(
        self,
    ):
        """
        Test that name and or display_picture_url keyword arguments passed to User constructor are set as
        attributes on user.
        :return: None
        """

        faker = Faker()

        name, display_picture_url = "Some name", "https://some_display_picture.url"

        new_user = User(name, display_picture_url)

        self.assertNotEqual(new_user.name, faker.name())
        self.assertNotEqual(new_user.display_picture_url, faker.image_url())

        self.assertEqual(new_user.name, name)
        self.assertEqual(new_user.display_picture_url, display_picture_url)

    def test_user_role_attribute_is_Role_NOT_SET_at_initialisation(self) -> None:
        """
        Test that the user role attribute is unset (Role.NOT_SET) at initialisation

        :return: None
        """
        self.assertEqual(self.user.role, Role.NOT_SET)

    def test_user_role_getter_returns_user_role_value(self) -> None:
        """
        Test that initialised user object's getter for role returns expected value

        :return: None
        """
        self.assertIsInstance(self.user.role, Role)

    def test_user_role_setter_sets_user_role_value(self) -> None:
        """
        Test that initialised user object's setter for role sets the supplied role

        :return: None
        """
        self.user.role = Role.PUBLISHER
        self.assertTrue(self.user.role, Role.PUBLISHER)

    def test_user_role_getter_and_setter_are_properties(self) -> None:
        """
        Test that User object getter and setter are properties

        :return: None
        """
        self.assertIsInstance(User.role, property)

    def test_role_setter_only_accepts_Role_object_argument(self) -> None:
        """
        Test that initialised User role setter only accepts Role objects

        :return: None
        """
        self.user._User__role = "Some role"

        self.assertRaises(AssertionError, lambda: self.user.role)

    @unittest.skipIf(
        len(Role.__members__) < 2,
        "Not Enough Roles (i.e. Role Enum Members) To Perform This Test!",
    )
    def test_user_set_random_role_method_randomly_selects_role_on_user_instance(
        self,
    ) -> None:
        """
        Test if the set_random_role method on the initialised user object changes the role of
        the user object.

        WARNING:
            This test is more of a regression test, and it essentially exists to protect the set_random_role method.
            Because of the relative unpredictability of the usage of the random module here, a more statistical
            distribution approach is employed to test that the method does perform as vaguely expected.

            THIS IN NO WAY IS A TEST OF random.choice() or any such variation. Since future refactors and abstractions
            may consume from the set_random_role method, this is just a sanity test to guarantee that regardless of the
            future refactors done to the source code, random selection is guaranteed.
        :return: None
        """
        role_state_count = Counter()

        for _ in range(len(Role.__members__) * 10):
            self.user.set_random_role()
            role_state_count[self.user.role] += 1

        selected_roles = [role for role, count in role_state_count.items() if count > 0]
        self.assertTrue(
            len(selected_roles) > 1,
            "Expected more than one role to be randomly selected.",
        )

    def test_user_can_be_initialised_with_particular_role(self) -> None:
        """
        Test that User object can be initialised with a particular role.

        :return: None
        """
        PUBLISHER, SUBSCRIBER = Role.PUBLISHER, Role.SUBSCRIBER

        publisher_user = User.with_role(PUBLISHER)
        subscriber_user = User.with_role(SUBSCRIBER)

        self.assertEqual(publisher_user.role, PUBLISHER)
        self.assertEqual(subscriber_user.role, SUBSCRIBER)

    @unittest.skipIf(
        len(Role.__members__) < 2,
        "Not Enough Roles (i.e. Role Enum Members) To Perform This Test!",
    )
    def test_user_can_be_initialised_with_random_role(self) -> None:
        """
        Test that User object can be initialised with random role.
        :return: None
        """

        # If the list of roles to make a random choice from is not supplied raise, ValueError

        role_state_count, ROLE_OPTIONS = Counter(), [Role.PUBLISHER, Role.NOT_SET]

        for _ in range(len(Role.__members__) * 4):
            self.user.set_random_role()
            role_state_count[User.from_role_options(ROLE_OPTIONS).role] += 1

        selected_roles = [role for role, count in role_state_count.items() if count > 0]
        self.assertTrue(
            len(selected_roles) >= 2,
            "Expected more than one role to be randomly selected.",
        )


class TestUserAsyncioMethodsTestCase(unittest.IsolatedAsyncioTestCase):
    """
    Test case class for testing functionalities of the user class utilising asyncio.
    """

    user = User()

    async def test_user_generate_message_method_calls_google_gemini_api_method_to_generate_message(
        self,
    ) -> None:
        """
        Test that the User object generate method returns some non-empty string result which is also the
        result of the Google Gemini API call.
        :return: None
        """
        message_context = "Some message context"
        user_model_mock = patch(
            "google.generativeai.GenerativeModel.generate_content_async"
        ).start()

        user_model_mock.return_value = SimpleNamespace(
            text="some generated message"
        )  # we need the text attribute implemented at AsyncGenerateContentResponse
        generated_message = await self.user.generate_message(message_context)

        user_model_mock.assert_called_once_with(message_context)

        self.assertEqual(generated_message, "some generated message")

        self.assertNotEqual(len(generated_message.strip()), 0)
