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

    @patch('sys.argv', ['main.py', *[other_argv for other_argv in Faker().sentence().split(" ")]])
    def test_program_prints_usage_instructions_on_invalid_input(self) -> None:
        """
        Test that the program prints usage instructions to terminal on
        wrong/invalid input.

        :return: None
        """

        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip(), MAIN_USAGE_TEXT.strip())

    @patch('sys.argv', ['main.py'])
    @patch('builtins.input', return_value="")
    def test_program_collects_preliminary_information_at_start(self, *_) -> None:
        """
        Test that program queries user for certain information at start.

        :return: None
        """

        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[0],
                             "Enter comma separated list of telegram phone numbers:")

    @patch('sys.argv', ['main.py'])
    @patch('builtins.input', return_value='invalid_phone_number')
    def test_program_quits_with_failure_message_on_invalid_input(self, *_) -> None:
        """
        Test that program quits with failure message on receipt of invalid phone number(s) from user
        :return: None
        """

        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[1],
                             "Invalid phone numbers. All phone numbers must be comma separated and each must include country code (+)")

    @patch('sys.argv', ['main.py'])
    @patch('builtins.input', return_value="+1(234) 567-8901")
    def test_program_asks_for_group_chat_context_after_supplying_valid_phone_numbers(self, *_) -> None:
        """
        Test that program asks for group chat context (i.e. nature of chats on the group chat) after
        user supplies valid phone number(s)

        :return: None
        """
        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[1], "Enter group chat context:")
