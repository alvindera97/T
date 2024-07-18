"""
Module for tests on the main entry module of the program.

This module contains test cases for source code contained at ROOT_DIR.main

Classes:
  TestMain
"""
import sys
import unittest
from io import StringIO

from faker import Faker

from main import main, MAIN_USAGE_TEXT


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

        captured_output = StringIO()
        sys.stdout = captured_output

        main(sys.argv)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue().strip()

        self.assertEqual(output, MAIN_USAGE_TEXT.strip())

