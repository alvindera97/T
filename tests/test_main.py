"""
Module for tests on the main entry module of the program.

This module contains test cases for source code contained at ROOT_DIR.main

Classes:
  TestMain
"""
import sys
import unittest
from unittest.mock import patch

from faker import Faker

from main import main, MAIN_USAGE_TEXT
from utils.context_managers import CaptureTerminalOutput


class TestMain(unittest.TestCase):
    """Test case for tests for main entry point of program"""

    def test_program_prints_usage_instructions_on_invalid_input(self) -> None:
        """
        Test that the program prints usage instructions to terminal on
        wrong/invalid input.

        :return: None
        """
        faker = Faker()
        sys.argv = ['main.py', *[other_argv for other_argv in faker.sentence().split(" ")]]

        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip(), MAIN_USAGE_TEXT.strip())

    def test_program_collects_preliminary_information_at_start(self) -> None:
        """
        Test that program queries user for certain information at start.

        :return: None
        """
        sys.argv = ['main.py']

        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip(), "Enter comma separated list of telegram phone numbers:")

    @patch('builtins.input', return_value='invalid_phone_number')
    def test_program_quits_with_failure_message_on_invalid_input(self, *_) -> None:
        """
        Test that program quits with failure message on receipt of invalid phone number(s) from user
        :return: None
        """

        sys.argv = ['main.py']

        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[1],
                             "Invalid phone number. All phone numbers must include country code (+)")
