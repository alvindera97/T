"""
Module for tests on utilities (utils)

This module contains test cases for testing source code at the utils pacakge

Classes:
  UtilsTestCase
"""
import unittest

from utils.context_managers import CaptureTerminalOutput


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
