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

    sys.argv = ['main.py']

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

    @patch('builtins.input', return_value="+1(234) 567-8901")
    def test_program_asks_for_group_chat_context_after_supplying_valid_phone_numbers(self, *_) -> None:
        """
        Test that program asks for group chat context (i.e. nature of chats on the group chat) after
        user supplies valid phone number(s)

        :return: None
        """
        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[1], "Enter group chat context (mandatory):")

    @patch('builtins.input', side_effect=["+1(234) 567-8901", "Hello world group", "", ""])
    def test_program_prompts_for_group_chat_link_after_receiving_valid_group_chat_context(self, *_) -> None:
        """
        Test that program prompts for group chat link after supply of group context.

        :return: None
        """
        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[2], "Enter group chat link:")

    @patch('builtins.input', side_effect=["+1(234) 567-8901", ""])
    def test_program_prints_quit_message_after_receiving_no_group_chat_context(self, *_) -> None:
        """
        Test that program prints quit text after receiving no group chat context.

        :return: None
        """
        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[2],
                             "Group chat context required but not supplied, quiting...")

    @patch('builtins.input', side_effect=["+1(234) 567-8901", "Hello world group", "https://t.me/someGroupChat"])
    def test_program_prints_initialisation_message_after_receiving_valid_group_chat_link(self, *_) -> None:
        """
        Test that program prints initialisation text after supply of valid group chat link.

        *** A LITTLE HEADS UP HERE ABOUT TELEGRAM GROUP CHAT LINKS: ***

        Since telegram group chat link structures are properly and popularly known at this point,
        it would make a world of convenience if invalid links are caught as early as possible.
        However, this would mean potentially pinging telegram at init-time (or whenever its convenient)
        to ensure that the link supplied is valid.

        - If a network ping with Telegram is used, it may potentially slow down testing
          or in extreme (rare) cases cause failed/erroneous tests if telegram's servers
          are unreachable or for some reason telegram's servers aren't able to correctly
          validate a given link.
        - If a regular expression (Regex) utility is used for this check, then it means that
          maintainers have to keep track of changes to telegram's public API and then update
          relevant mechanisms.

        :return: None
        """
        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[3], "Initialising...")

    @patch('builtins.input', side_effect=["+1(234) 567-8901", "Hello world group", ""])
    def test_program_prints_quit_message_after_not_receiving_group_chat_link(self, *_) -> None:
        """
        Test that program prints quit text after not receiving group chat link.

        :return: None
        """
        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip().split("\n")[3],
                             "Group chat link required but not supplied, quiting...")
