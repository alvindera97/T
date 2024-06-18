"""
Module for tests on [user] roles.

This module contains test cases for testing user roles and their functionality.

Classes:
  TestRolesTestCase: Provides test methods for unit tests on user roles.

Methods:
  setUp(): Prepares test environment before each test.
  tearDown(): Cleans up test environment after each test.
  setUpClass(): Defines code executions before start of tests.
  test_role_enum_class_exists(): Tests if Role class enum exists.
  test_role_is_an_enum_instance_is_of_roles_class(): Test that that Role instance is of the Role class.
  test_role_enum_has_both_publisher_and_subscriber_representation_entities(): Test Role has Subscriber & Publisher attrs
"""
import inspect
import unittest
from enum import Enum

from role import Role


class TestRolesTestCase(unittest.TestCase):
    """
    Test case class for tests for user roles.
    """

    @classmethod
    def setUpClass(cls):
        """
        Method defining executions before starting of tests in the class.

        Differs from self.setUp() as self.setUp() is called before every test
        while self.setUpClass() is called before start of all the tests in the
        class exactly once.
        :return:
        """
        super().setUpClass()
        cls.role = Role

    def setUp(self) -> None:
        """
        Method defining what must be run before each test method within this class.
        :return: None
        """
        super().setUp()

    def teatDown(self) -> None:
        """
        Method defining actions after each test method within this class.
        :return: None
        """
        super().tearDown()

    def test_role_enum_class_exists(self) -> None:
        """
        Tests if the Role enum class exists.
        :return: None
        """
        self.assertTrue(inspect.isclass(Role))

    def test_role_is_an_enum_instance_is_of_roles_class(self):
        """
        Tests if the role object is of type Enum class
        :return: None
        """
        self.assertEqual(type(self.role), type(Enum))

    def test_role_enum_has_both_publisher_and_subscriber_representation_entities(self):
        self.assertEqual(self.role.PUBLISHER.value, 1)
        self.assertEqual(self.role.SUBSCRIBER.value, 2)


if __name__ == "__main__":
    unittest.main()
