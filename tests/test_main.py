"""
Module for tests on the main entry module of the program.

This module contains test cases for source code contained at ROOT_DIR.main

Classes:
  TestMain
  TestInitialiseComments
"""
import sys
import unittest
from unittest.mock import patch

from faker import Faker

from main import main, MAIN_USAGE_TEXT, initialise_comments
from utils.context_managers import CaptureTerminalOutput


class TestMain(unittest.TestCase):
    """Test case for tests at main entry point of program"""

    sys.argv = ['main.py']

    def setUp(self):
        self._initialise_comments_patcher = patch('main.initialise_comments')
        self.initialise_comments_mock = self._initialise_comments_patcher.start()

    def tearDown(self):
        self.initialise_comments_mock.reset_mock()
        self._initialise_comments_patcher.stop()

    @patch('sys.argv', ['main.py', *[other_argv for other_argv in Faker().sentence().split(" ")]])
    def test_program_prints_usage_instructions_on_invalid_input(self, *_) -> None:
        """
        Test that the program prints usage instructions to terminal on
        wrong/invalid input.

        :return: None
        """

        with CaptureTerminalOutput() as output:
            main(sys.argv)
            self.assertEqual(output.getvalue().strip(), MAIN_USAGE_TEXT.strip())

        self.initialise_comments_mock.asssert()

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

        self.initialise_comments_mock.assert_not_called()

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

        self.initialise_comments_mock.assert_not_called()

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

        self.initialise_comments_mock.assert_called_once_with("https://t.me/someGroupChat", "Hello world group",
                                                              ["+1(234) 567-8901"])

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

        self.initialise_comments_mock.assert_not_called()


class TestInitialiseComments(unittest.TestCase):
    """Test case for tests at 'Red Carpet And Coin Toss Module'"""

    def test_initialise_comments_takes_group_link_group_context_and_phone_numbers_arguments_only(self) -> None:
        """

        :return: None
        """
        self.assertRaises(TypeError, lambda: initialise_comments())
        self.assertRaises(TypeError, lambda: initialise_comments(""))
        self.assertRaises(TypeError, lambda: initialise_comments("", ""))
        self.assertRaises(TypeError, lambda: initialise_comments(
            "",
            "",
            [],
            *[Faker().sentence().split(" ")]
        ))

    def test_initialise_comments_takes_arguments_of_expected_content_characteristics(self) -> None:
        """
        Test that arguments received are of expected content which includes content type (data type) and some sanity
        checks for stuff like group_context and group_link length (just for sanity checks).

        *** ANOTHER NOTE ON group_link: ***

        -  An invalid group link would be caught only at the point where there's a network failure while attempting
           to send a message to the group.
        :return: None
        """

        # Test invalid types raise exceptions

        self.assertRaises(TypeError, lambda: initialise_comments(1, "c", ["p"]))
        self.assertRaises(TypeError, lambda: initialise_comments("l", 1.1, phone_numbers=["p"]))
        self.assertRaises(TypeError, lambda: initialise_comments("l", "c", phone_numbers=""))

        # Sanity test for argument content sizes
        self.assertRaises(ValueError, lambda: initialise_comments("", "c", phone_numbers=["p"]))
        self.assertRaises(ValueError, lambda: initialise_comments("l", "", phone_numbers=["p"]))
        self.assertRaises(ValueError, lambda: initialise_comments("l", "c", phone_numbers=[]))

        # TODO: Add Custom Exceptions for better readability & developer experience
