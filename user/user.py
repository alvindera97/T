"""
User module (also referable to as 'Client' module)

This module contains the class and module definitions for the User (Client) entity.

Classes:
  User

"""
from __future__ import annotations

import asyncio
import random
from typing import List, NoReturn, Union, Coroutine

from aiokafka import AIOKafkaProducer

from role import Role
from utils.exceptions import OperationNotAllowedException


class User:
    """
    Class definition for the User entity
    """

    __role: Role = Role.NOT_SET
    __role_members: List[Role] = list(Role.__members__.values())

    def __init__(self) -> None:
        super().__init__()
        self.__producer = asyncio.run(self.generate_producer_object())

    @staticmethod
    async def generate_producer_object() -> AIOKafkaProducer:
        """
        Coroutine that creates an AIOKafkaProducer and returns the Producer instance.

        :return: AIOKafkaProducer instance
        """
        return AIOKafkaProducer(bootstrap_servers='localhost:9092')

    @staticmethod
    def with_role(role: Role) -> Union[User, NoReturn]:
        """
        Constructor to create new User with supplied Role
        :param role: The role to set user to.
        :return:  User or NoReturn (NoReturn because the function may never return as it can raise an exception.)
        """
        try:
            new_user = User()
            new_user.role = role
            return new_user
        except KeyError as e:
            raise ValueError(f'{e.__str__()} must be supplied as keyword argument with this method.')

    @staticmethod
    def from_role_options(roles: List[Role]) -> Union[User, NoReturn]:
        """
        Constructor to create new Role selected from random selection of supplied Role objects in 'roles'
        :param roles: List of roles to make a random selection from.
        :return:  User or NoReturn (NoReturn because the function may never return as it can raise an exception.)
        """
        try:
            new_user = User()
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

    @property
    def producer(self) -> AIOKafkaProducer:
        """Getter for User producer"""
        assert isinstance(self.__producer, AIOKafkaProducer)
        return self.__producer

    @producer.setter
    def producer(self, *args):
        raise OperationNotAllowedException("User producer attribute is private and is intended to be unmodifiable.")

    @producer.deleter
    def producer(self, *args, **kwargs):
        raise OperationNotAllowedException("User producer attribute is private and is intended to be unmodifiable.")

    def set_random_role(self) -> None:
        """
        Set random role on instance
        :return: None
        """
        self.role = random.SystemRandom().choice(self.__role_members)

    def __del__(self):
        self.producer._closed = True
