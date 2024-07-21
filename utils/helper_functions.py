"""
Utilities helper functions module

This module contains code for utils (utilities) which are primarily helper functions.
"""

from typing import List, Optional

import phonenumbers


def extract_phone_numbers(input_string) -> List[Optional[str]]:
    """
    Given a string input (ideally a string of comma separated phone numbers), this
    function returns a list of the string phone numbers contained in the input
    string (input_string); these phone numbers should include country code.

    If the input string is invalid, this function immediately returns an empty list.

    :param input_string: Ideally a comma separated list of phone numbers
    :return:
    """

    phone_numbers = [num.strip() for num in input_string.split(',')]
    valid_numbers = []

    for number in phone_numbers:
        try:
            parsed_number = phonenumbers.parse(number)
            if phonenumbers.is_valid_number(parsed_number):
                valid_numbers.append(number)
            else:
                return []
        except phonenumbers.NumberParseException:
            return []

    return valid_numbers
