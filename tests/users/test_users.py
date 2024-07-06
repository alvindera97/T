"""
Module for tests on user / client.

This module contains test cases or testing the "User" (otherwise called Client) entity
and all related functionality.

Classes:
  TestUserTestCase
"""
import inspect
import unittest
from collections import Counter

from telethon import TelegramClient

from role import Role
from user import User


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
        cls.user = User(12345, "|")

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

    def test_user_has_telethon_client_attribute(self) -> None:
        """
        Test if User class has an attribute for Telegram client.

        :return: None
        """
        self.assertIsNotNone(self.user.telegram_client)
        self.assertIsInstance(self.user.telegram_client, TelegramClient)

    def test_user_has_role_attribute(self) -> None:
        """
        Test that initialized user object has role attribute.

        :return: None
        """
        self.assertTrue(hasattr(User, 'role'))

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

    @unittest.skipIf(len(Role.__members__) < 2, "Not Enough Roles (i.e. Role Enum Members) To Perform This Test!")
    def test_user_set_random_role_method_randomly_selects_role_on_user_instance(self) -> None:
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

        for _ in range(len(Role.__members__) * 2):
            self.user.set_random_role()
            role_state_count[self.user.role] += 1

        selected_roles = [role for role, count in role_state_count.items() if count > 0]
        self.assertTrue(len(selected_roles) > 1, "Expected more than one role to be randomly selected.")

    def test_user_can_be_initialised_with_particular_role(self) -> None:
        """
        Test that User object can be initialised with a particular role.

        :return: None
        """
        PUBLISHER, SUBSCRIBER = Role.PUBLISHER, Role.SUBSCRIBER

        publisher_user = User.with_role(PUBLISHER, api_id=12345, api_hash="|")
        subscriber_user = User.with_role(SUBSCRIBER, api_id=12345, api_hash="|")

        self.assertEqual(publisher_user.role, PUBLISHER)
        self.assertEqual(subscriber_user.role, SUBSCRIBER)

    def test_with_role_method_raises_exceptions_on_missing_kwargs(self) -> None:
        """
        Test that if required keyword arguments are missing in the .with_role() call,
        it raises the appropriate exception.
        :return: None
        """
        with self.assertRaises(ValueError) as context:
            User.with_role(Role.NOT_SET)

        self.assertEqual(str(context.exception), "api_id must be supplied as keyword argument with this method.")

    @unittest.skipIf(len(Role.__members__) < 2, "Not Enough Roles (i.e. Role Enum Members) To Perform This Test!")
    def test_user_can_be_initialised_with_random_role(self) -> None:
        """
        Test that User object can be initialised with random role.

        In this case the constructor should be able to take stock of what roles the user intends on a random choice being
        made of at initialisation of the object. Another important check that happens is that:

            IN THE CASE WHERE THE USER SUPPLIES 'role' FOR A FIXED ROLE AT INITIALISATION, THE CONSTRUCTOR SHOULD RAISE
            AN EXCEPTION TO INFORM THAT A USER CAN EITHER:

            1. BE UNSET (default)
            2. BE SET TO A SUPPLIED ROLE (which can also be Role.NOT_SET) AT INITIALISATION (via __init__ 'role' argument).
            3. BE SET TO RANDOM ROLE FROM GIVEN LIST OF ROLE OBJECTS (via the __init__ 'from_roles' argument)


        Only one of such initialisation workflows is valid.
        :return: None
        """
        self.assertRaises(ValueError,
                          lambda: User(12345, '|', role=Role.PUBLISHER, from_role=[Role.PUBLISHER, Role.NOT_SET]))
        self.assertRaises(ValueError,
                          lambda: User(12345, '|', role=Role.PUBLISHER, from_role=[]))

        role_state_count, ROLE_OPTIONS = Counter(), [Role.PUBLISHER, Role.NOT_SET]

        for _ in range(len(Role.__members__) * 4):
            self.user.set_random_role()
            role_state_count[User(12345, api_hash='|', from_role=ROLE_OPTIONS).role] += 1

        selected_roles = [role for role, count in role_state_count.items() if count > 0]
        self.assertTrue(len(selected_roles) >= 2, "Expected more than one role to be randomly selected.")
