"""
Module for tests on user / client.

This module contains test cases or testing the "User" (otherwise called Client) entity
and all related functionality.

Classes:
  TestUserTestCase

Methods:
  setUp(): Prepares test environment before each test.
  tearDown(): Cleans up test environment after each test.
  test_user_class_exists(): Tests if class defining User entity exists.
"""
import inspect
import unittest


class TestUserTestCase(unittest.TestCase):
    """
    Test case class for tests for User entity
    """

    def setUp(self) -> None:
        """
        Method defining what must be run before each test method within this class.
        :return: None
        """
        super().setUp()

    def tearDown(self):
        """
        Method defining actions after each test method within this class.
        :return: None
        """
        super().tearDown()

    def test_user_class_exists(self) -> None:
        """
        Tests if user class exists
        :return: None
        """
        self.assertTrue(inspect.isclass(User))
