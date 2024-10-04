"""
Controller module (also referable to as 'Application Controller' module)

This module contains the class and module definitions for the Application Controller
"""

from __future__ import annotations
import random
from typing import Optional, List

import websockets

from role import Role
from user import User
from .kafka_manager_def import KafkaManagerFactory


class Controller:
    """
    Class definition for application controller.
    """

    ws_url = None
    __websocket: Optional[websockets.WebSocketClientProtocol] = None

    @staticmethod
    async def initialise(
        number_of_users: int, ws_url: str, chat_context: str
    ) -> Controller:
        """
        Constructor for Controller object.

        The controller performs lightly as a Controller from the MVC Design Pattern
        https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller
        :param number_of_users:  Number of users to participate in application lifecycle
        :param ws_url: Web socket url for Controller to interact with.
        :param chat_context: Group chat context
        """

        cls = Controller()

        assert (type(number_of_users) is int and number_of_users > 0) and type(
            chat_context
        ) is str

        cls.ws_url = ws_url
        cls.chat_context = chat_context
        chat_uuid = cls.ws_url.split("/")[-1]
        cls.kafka_manager = KafkaManagerFactory.create_base_kafka_manager(
            number_of_users
        )
        cls.participating_users: List[User] = [User() for _ in range(number_of_users)]

        for consumer in cls.kafka_manager.consumers:
            consumer.subscribe([chat_uuid])

        cls.first_publisher: User = random.choice(cls.participating_users)

        cls.first_publisher.role = Role.PUBLISHER
        await cls.connect_ws()
        return cls

    @property
    def websocket(self):
        """Controller websocket getter."""
        return self.__websocket

    @websocket.setter
    def websocket(self, new_websocket_value):
        assert type(new_websocket_value) is websockets.WebSocketClientProtocol
        self.__websocket = new_websocket_value

    async def connect_ws(self, message=None):
        """
        Connects controller to websocket with web socket url

        :param message: Optional message to send to the websocket
        :return:
        """
        if not message:
            self.__websocket = await websockets.connect(self.ws_url)
        else:
            async with websockets.connect(self.ws_url) as websocket:
                await websocket.send(message)
