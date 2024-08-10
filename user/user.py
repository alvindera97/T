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

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from role import Role
from utils.exceptions import OperationNotAllowedException

import google.generativeai as genai
import os


model = genai.GenerativeModel('gemini-1.0-pro-latest')
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class User:
    """
    Class definition for the User entity
    """

    __role: Role = Role.NOT_SET
    __role_members: List[Role] = list(Role.__members__.values())

    def __init__(self, name: str = "", display_picture_url: str = "") -> None:
        """
        Constructor for User object.

        The user object can operate as a Kafka producer or a Kafka comsumer.

        :param name: String name attribute for user
        :param display_picture_url: String display picture url for user
        """

        # TODO: add checks to ensure that passed display_picture_url kwarg is valid image resource url

        super().__init__()
        self.name = name
        self.display_picture_url = display_picture_url
        self.__producer = asyncio.run(self.__generate_producer_object())
        self.__consumer = asyncio.run(self.__generate_consumer_object())

    @classmethod
    async def __generate_producer_object(cls) -> AIOKafkaProducer:
        """
        Coroutine that creates an AIOKafkaProducer and returns the Producer instance.

        :return: AIOKafkaProducer instance
        """
        return AIOKafkaProducer(bootstrap_servers="localhost:9092")

    @classmethod
    async def __generate_consumer_object(cls) -> AIOKafkaConsumer:
        """
        Coroutine that creates an AIOKafkaConsumer and returns the Consumer instance
        :return: AIOKafkaConsumer instance
        """
        return AIOKafkaConsumer(bootstrap_servers="localhost:9092")

    @classmethod
    def with_role(cls, role: Role) -> Union[User, NoReturn]:
        """
        Constructor to create new User with supplied Role
        :param role: The role to set user to.
        :return:  User or NoReturn (NoReturn because the function may never return as it can raise an exception.)
        """
        try:
            new_user = cls()
            new_user.role = role
            return new_user
        except KeyError as e:
            raise ValueError(f'{e.__str__()} must be supplied as keyword argument with this method.')

    @classmethod
    def from_role_options(cls, roles: List[Role]) -> Union[User, NoReturn]:
        """
        Constructor to create new Role selected from random selection of supplied Role objects in 'roles'
        :param roles: List of roles to make a random selection from.
        :return:  User or NoReturn (NoReturn because the function may never return as it can raise an exception.)
        """
        try:
            new_user = cls()
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

    @property
    def consumer(self) -> AIOKafkaConsumer:
        """Getter for User consumer"""
        assert isinstance(self.__consumer, AIOKafkaConsumer)
        return self.__consumer

    @consumer.setter
    def consumer(self, *args):
        raise OperationNotAllowedException("User consumer attribute is private and is intended to be unmodifiable.")

    @consumer.deleter
    def consumer(self, *args, **kwargs):
        raise OperationNotAllowedException("User consumer attribute is private and is intended to be unmodifiable.")

    def set_random_role(self) -> None:
        """
        Set random role on instance
        :return: None
        """
        self.role = random.SystemRandom().choice(self.__role_members)

    async def generate_message(self, message_context: str) -> Union[str, NoReturn]:
        """
        Generate message from LLM given message_context. Message context stands for the context in which
        a user object generates messages / responses / reactions to.

        :param message_context: String message context.
        :return: String message generated by LLM
        """

        message = await model.generate_content_async(message_context)
        return message.text

    def __del__(self):
        asyncio.run(self.consumer.stop())
        asyncio.run(self.producer.stop())
