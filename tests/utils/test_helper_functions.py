"""
Module for tests on utilities (utils)

This module contains test cases for testing source code at the utils pacakge

Classes:
  UtilsTestCase
"""
import unittest

from utils.context_managers import CaptureTerminalOutput
from utils.helper_functions import extract_phone_numbers


class UtilsTestCase(unittest.TestCase):
    """
    Test case class for utilities contained at utils package
    """

    def test_capture_output_context_manager_captures_correct_output(self) -> None:
        """
        Test that the context manager for capturing terminal captures terminal output
        correctly.

        :return: None
        """
        with CaptureTerminalOutput() as captured_output:
            print("hello world")

            captured_text = captured_output.getvalue()
            expected_output = "hello world\n"
            self.assertEqual(captured_text, expected_output)

    def test_capture_output_context_manager_stringio_is_closed(self) -> None:
        """
        Test that capture output context manager StringIO is closed; good for freeing up
        system resources.

        :return: None
        """
        capture = CaptureTerminalOutput()
        with capture as captured_output:
            (lambda: None)()

        self.assertTrue(captured_output.closed)

    def test_extract_phone_numbers_function_on_valid_input(self) -> None:
        """
        Test that get_phone_numbers() returns all phone numbers on valid
        string input

        :return: None
        """
        self.assertEqual(
            extract_phone_numbers("+1(234) 567-8901"),
            ["+1(234) 567-8901"]
        )

    def test_extract_phone_numbers_function_on_invalid_input(self) -> None:
        """
        Test that get_phone_numbers() returns empty list on invalid string input
        :return: None
        """

        self.assertEqual(
            extract_phone_numbers("+123 456 7890, +1(234) 567-8901"),
            []
        )

    def test_extract_phone_numbers_function_on_empty_input(self) -> None:
        """
        Test that get_phone_numbers() returns empty list on empty input
        :return: None
        """
        self.assertEqual(
            extract_phone_numbers(""),
            []
        )

    def test_extract_phone_numbers_function_on_input_without_commas(self) -> None:
        """
        Test that get_phone_numbers() returns empty list on input without commas
        :return: None
        """

        self.assertEqual(
            extract_phone_numbers("not_a_phone_number"),
            []
        )

        self.assertEqual(
            extract_phone_numbers("+123 456 7890" "+12 345-6789"),
            []
        )
