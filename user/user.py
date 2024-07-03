"""
User module (also referable to as 'Client' module)

This module contains the class and module definitions for the User (Client) entity.

Classes:
  User

"""
import random
from typing import List

from telethon import TelegramClient

from role import Role


class User:
    """
    Class definition for the User entity
    """

    __role: Role = Role.NOT_SET
    __role_members: List[Role] = list(Role.__members__.values())

    def __init__(self, api_id: int, api_hash: str) -> None:
        """
        Class initializer
        :param api_id: Telegram client API ID (issued by telegram)
        :param api_hash: Telegram client API_HASH for corresponding API_ID
        :return: None
        """

        self.telegram_client = TelegramClient("default", api_id, api_hash)

    @property
    def role(self) -> Role:
        """
        Getter for User role
        :return: None
        """
        assert isinstance(self.__role, Role)
        return self.__role

    @role.setter
    def role(self, role) -> None:
        """
        Setter for User role
        :param role: user role
        :return: None
        """
        assert isinstance(role, Role)
        self.__role = role

    def set_random_role(self) -> None:
        """
        Set random role on instance
        :return: None
        """
        self.role = random.SystemRandom().choice(self.__role_members)
