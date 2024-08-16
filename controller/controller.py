"""
Controller module (also referable to as 'Application Controller' module)

This module contains the class and module definitions for the Application Controller
"""
import random

from role import Role
from user import User


class Controller:
    """
    Class definition for application controller.
    """
    ws_url = None
    is_connected = False

    def __init__(self, number_of_users: int, ws_url: str) -> None:
        """
        Constructor for Controller object.

        The controller performs lightly as a Controller from the MVC Design Pattern
        https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller
        :param number_of_users:  Number of users to participate in application lifecycle
        :param ws_url: Web socket url for Controller to interact with.
        """

        assert isinstance(number_of_users, int)
        assert number_of_users > 0

        self.ws_url = ws_url
        self.participating_users = [User() for _ in range(number_of_users)]
        self.first_publisher: User = random.choice(self.participating_users)

        self.first_publisher.role = Role.PUBLISHER
