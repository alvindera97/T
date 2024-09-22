"""
Module for tests on utility exceptions.

This module contains test cases for testing the exceptions module in
the utilities package and all related functionality to the
exception module.

Classes:
  TestOperationNotAllowedException
"""

import unittest

from utils.exceptions import OperationNotAllowedException


class TestOperationNotAllowedException(unittest.TestCase):
    """
    Test case class for tests on OperationNotAllowedException utility
    exception.
    """

    def test_exception_is_raised_with_default_message(self) -> None:
        """
        Test that OperationNotAllowedException is raised with default
        message without passing args to the call.
        :return: None
        """
        with self.assertRaises(OperationNotAllowedException) as context:
            raise OperationNotAllowedException()

        self.assertEqual(context.exception.message, "This operation is not allowed.")

    def test_exception_is_raised_with_set_custom_message(self) -> None:
        """
        Test that OperationNotAllowedException(custom_message) is raised with the set
        custom message.
        :return: None
        """

        with self.assertRaises(OperationNotAllowedException) as context:
            raise OperationNotAllowedException("This operation is forbidden!")

        self.assertEqual(context.exception.message, "This operation is forbidden!")
