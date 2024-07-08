"""
User module (also referable to as 'Client' module)

This module contains the class and module definitions for the User (Client) entity.

Classes:
  User

"""
from __future__ import annotations
import random
from typing import List, Optional, NoReturn, Union

from telethon import TelegramClient
from telethon.sessions import StringSession


from role import Role


class User:
    """
    Class definition for the User entity
    """

    __role: Role = Role.NOT_SET
    __role_members: List[Role] = list(Role.__members__.values())

    def __init__(self, api_id: int, api_hash: str, session_token: Optional[str] = None) -> None:
        """
        Class initializer
        :param api_id: Telegram client API ID (issued by telegram)
        :param api_hash: Telegram client API_HASH for corresponding API_ID
        :return: None
        """

        self.telegram_client = TelegramClient(StringSession(session_token), api_id, api_hash)

    @classmethod
    def with_role(cls, role: Role, **kwargs) -> Union[User, NoReturn]:
        """
        Constructor to create new User with supplied Role
        :param role: The role to set user to.
        :return:  User or NoReturn (NoReturn because the function may never return as it can raise an exception.)
        """
        try:
            new_user = User(kwargs['api_id'], kwargs['api_hash'])
            new_user.role = role
            return new_user
        except KeyError as e:
            raise ValueError(f'{e.__str__()} must be supplied as keyword argument with this method.')

    @classmethod
    def from_role_options(cls, roles: List[Role], **kwargs) -> Union[User, NoReturn]:
        """
        Constructor to create new Role selected from random selection of supplied Role objects in 'roles'
        :param roles: List of roles to make a random selection from.
        :return:  User or NoReturn (NoReturn because the function may never return as it can raise an exception.)
        """
        try:
            new_user = User(kwargs['api_id'], kwargs['api_hash'])
            new_user.role = random.choice(roles)
            return new_user
        except KeyError as e:
            raise ValueError(f'{e.__str__()} must be supplied as keyword argument with this method.')
        except (IndexError, AssertionError):
            raise ValueError(f'You must supply a non-empty list of Role objects, not {roles}')

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
