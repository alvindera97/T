"""
Controller module (also referable to as 'Application Controller' module)

This module contains the class and module definitions for the Application Controller
"""
from user import User


class Controller:
    """
    Class definition for application controller.
    """

    def __init__(self, number_of_users: int) -> None:
        """
        Constructor for Controller object.

        The controller performs lightly as a Controller from the MVC Design Pattern
        https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller
        :param number_of_users:  Number of users to participate in application lifecycle
        """

        assert isinstance(number_of_users, int)
        assert number_of_users > 0

        self.participating_users = [User() for _ in range(number_of_users)]