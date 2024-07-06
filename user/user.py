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

    def __init__(self, api_id: int, api_hash: str, session_token: Optional[str] = None, role: Optional[Role] = None,
                 from_role: List[Optional[Role]] = None) -> None:
        """
        Class initializer
        :param api_id: Telegram client API ID (issued by telegram)
        :param api_hash: Telegram client API_HASH for corresponding API_ID
        :param session_token: Telegram string session token for user, see https://docs.telethon.dev/en/stable/concepts/sessions.html#string-sessions
        :param role: Role initialised user assumes
        :return: None
        """

        self.telegram_client = TelegramClient(StringSession(session_token), api_id, api_hash)
        if role:
            if from_role is not None:
                raise ValueError(
                    "You have supplied objects for both 'from_role' and 'role' which is forbidden.")
            self.role = role

        if from_role:
            if type(from_role) is not type(list()) or [k for k in
                                                       filter(lambda l: l not in Role.__members__.values(), from_role)]:
                raise ValueError("from_role must be a list of Role objects")
            self.role = random.SystemRandom().choice(from_role)

    @classmethod
    def with_role(cls, role: Role, **kwargs) -> Union[User, NoReturn]:
        """
        Constructor to create new User with supplied Role
        :param role: The role to set user to.
        :return:  User or NoReturn (NoReturn because the function may never return as it can raise an exception.)
        """
        EXPECTED_KWARGS = ['api_id', 'api_hash']  # this is not good design but will suffice for now

        for ek in EXPECTED_KWARGS:
            if not kwargs.get(ek):
                raise ValueError(f'{ek} must be supplied as keyword argument with this method.')

        new_user = User(kwargs['api_id'], kwargs['api_hash'])
        new_user.role = role
        return new_user

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
