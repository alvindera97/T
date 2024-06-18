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
"""
import inspect
import unittest

from telethon import TelegramClient

from user.user import User


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
