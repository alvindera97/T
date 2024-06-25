"""
Module for tests on user / client.

This module contains test cases or testing the "User" (otherwise called Client) entity
and all related functionality.

Classes:
  TestUserTestCase

Methods:
  setUp(): Prepares test environment before each test.
  tearDown(): Cleans up test environment after each test.
  setUpClass(): Defines code executions and attributes for all tests.
  test_user_class_exists(): Tests if class defining User entity exists.
  test_user_has_telegram_client_attribute(): Test if User class has Telegram client attribute
  test_user_has_role_attribute(): Test if User class has role attribute
  test_user_role_attribute_is_null_at_initialisation(): Test that user role has no value at initialisation
  test_user_role_getter_returns_user_role_value(): Test user roles getter returns appropriate value
  test_user_role_setter_sets_user_role_value(): Test user role setter sets given arg to the object instance
"""
import inspect
import unittest

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
        self.user._User__role = None

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

    def test_user_role_attribute_is_null_at_initialisation(self) -> None:
        """
        Test that the user role attribute is null at initialisation

        :return: None
        """
        self.assertIsNone(self.user._User__role)

    def test_user_role_getter_returns_user_role_value(self) -> None:
        """
        Test that initialised user object's getter for role returns expected value

        :return: None
        """
        self.user.role = Role.SUBSCRIBER
        self.assertEqual(self.user.role, Role.SUBSCRIBER)

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
