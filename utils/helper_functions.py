"""
Utilities helper functions module

This module contains code for utils (utilities) which are primarily helper functions.
"""

import re
from typing import List, Optional


def extract_phone_numbers(input_string) -> List[Optional[str]]:
    """
    Given a string input (ideally a string of comma separated phone numbers), this
    function returns a list of the string phone numbers contained in the input
    string (input_string); these phone numbers should include country code.

    If the input string is invalid, this function immediately returns an empty list.

    :param input_string: Ideally a comma separated list of phone numbers
    :return:
    """

    # Regex pattern for valid phone numbers with country code
    pattern = re.compile(r'^\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,4}$')

    phone_numbers = [num.strip() for num in input_string.split(',')]

    for number in phone_numbers:
        if not pattern.fullmatch(number):
            return []  # no need continuing here.

    return phone_numbers
