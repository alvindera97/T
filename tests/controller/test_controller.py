"""
Module for tests on application controller

This module contains test cases or testing the "Controller" (otherwise called Application Controller) entity
and all related functionality.

Classes:
  ApplicationControllerTestCase
"""
import random
import unittest

from controller import Controller


class ApplicationControllerTestCase(unittest.TestCase):
    """
    Test case class for Application Controller
    """

    def test_controller_constructor_has_array_of_unique_users_based_on_constructor_argument(self) -> None:
        """
        Test that the controller constructor takes in kwarg for number of users and populates participating_users
        attribute with number of unique User objects is specified by the keyword argument.
        :return: None
        """
        number_of_participating_users = random.randint(2, 10)
        controller = Controller(number_of_participating_users)

        self.assertEqual(len(set(controller.participating_users)), number_of_participating_users)


    def test_that_controller_raises_exception_on_nonsensical_input_for_number_of_participating_users(self) -> None:
        """
        Test that the controller constructor raises an exception when non int types or an int less than one is passed
        for number of participating users.

        :return: None
        """
        self.assertRaises(AssertionError, lambda: Controller(0))
        self.assertRaises(AssertionError, lambda: Controller(-1))
        self.assertRaises(AssertionError, lambda: Controller("0"))
