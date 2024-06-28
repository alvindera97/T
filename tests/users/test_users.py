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
  test_user_role_attribute_is_Role_NOT_SET_at_initialisation(): Test that user role is unset at initialisation
  test_user_role_getter_returns_user_role_value(): Test user roles getter returns appropriate value
  test_user_role_setter_sets_user_role_value(): Test user role setter sets given arg to the object instance
  test_role_setter_only_accepts_Role_object_argument(): Test user role setter only accepts Role object arguments.
  test_role_getter_only_returns_Role_objects(): Test user role getter only returns Role objects, else raise an exception
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
