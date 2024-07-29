"""
Main entry point of application

This module contains code calling setup, processing and tear down operations.
"""

import os
import sys
from typing import Optional, List

from user import User
from utils.helper_functions import extract_phone_numbers

MAIN_USAGE_TEXT: str = """Usage: python main.py

        PubSub Telegram Bot Comments

        Starts the application without any command-line arguments. This program manages comments using a PubSub architecture on Telegram.

        Before starting, ensure you have the following information ready:
        - Telegram group chat link where conversations will occur.
        - Phone numbers of group members who can receive OTPs for login (ensure these numbers can receive text messages).
        """


def main(system_argument: List[Optional[str]]):
    """
    Main entry point of program. This is usually gotten from sys.argv.
    Due to testing requirements at the moment until something more elegant is implemented,
    the system_arguments will not have default value, and it will be required to pass sys.argv to
    the function. Again, this is just to note that ideally,  system_argument is supplied from command line
    arguments executing this module.

    :param system_argument: List of program execution command line arguments (usually sys.argv)
    :return: None
    """
    if len(system_argument) > 1:
        print(MAIN_USAGE_TEXT)

    else:
        print("Enter comma separated list of telegram phone numbers:")
        PHONE_NUMBERS: List[str] = extract_phone_numbers(input())
        if not PHONE_NUMBERS:
            print(
                "Invalid phone numbers. All phone numbers must be comma separated and each must include country code (+)")
        else:
            print("Enter group chat context (mandatory):")
            group_chat_context = input().strip()
            if group_chat_context:
                print("Enter group chat link:")
                group_chat_link = input()
                if group_chat_link:
                    print("Initialising...")
                    initialise_comments(group_chat_link, group_chat_context, PHONE_NUMBERS)
                else:
                    print("Group chat link required but not supplied, quiting...")
            else:
                print("Group chat context required but not supplied, quiting...")


def initialise_comments(group_link: str, group_context: str, phone_numbers: List[str]) -> None:
    """
    Initialise comments essentially does 2 things:

    - Generates User objects from the phone numbers list
    - Passes group_link, group_context and a collection of User objects
      generated from phone_numbers to start_comments()

    :param group_link:
    :param group_context:
    :param phone_numbers:
    :return: None
    """
    if type(group_link) is not str or type(group_context) is not str or type(phone_numbers) is not list:
        raise TypeError(
            "Invalid types supplied. See help(initialise_comments) for information on argument types")

    if len(group_link.strip()) == 0 or len(group_context.strip()) == 0 or len(phone_numbers) == 0:
        raise ValueError(
            "Invalid content size! See help(initialise_comments) for more information on expected argument content.")

    users = [User(os.getenv('API_ID'), os.getenv('API_HASH')) for _ in range(len(phone_numbers))]
    start_comments(group_link, group_context, users)

def start_comments(*args):
    pass


if __name__ == '__main__':
    main(sys.argv)
