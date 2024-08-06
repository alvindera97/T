"""
Utility exceptions module.

This module contains custom exception classes.

Classes:
  OperationNotAllowedException
"""


class OperationNotAllowedException(Exception):
    """
    Exception notifying operator that an operation is not allowed or designed to
    not be possible.
    """

    def __init__(self, message="This operation is not allowed."):
        self.message = message
        super().__init__(self.message)
