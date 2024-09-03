"""
Controller module (also referable to as 'Application Controller' module)

This module contains the class and module definitions for the Application Controller
"""
import asyncio
import random
from typing import Optional, List

import websockets

from role import Role
from user import User


class Controller:
    """
    Class definition for application controller.
    """
    ws_url = None
    __websocket: Optional[websockets.WebSocketClientProtocol] = None

    def __init__(self, number_of_users: int, ws_url: str, chat_context: str) -> None:
        """
        Constructor for Controller object.

        The controller performs lightly as a Controller from the MVC Design Pattern
        https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller
        :param number_of_users:  Number of users to participate in application lifecycle
        :param ws_url: Web socket url for Controller to interact with.
        :param chat_context: Group chat context
        """

        assert type(number_of_users) is int
        assert type(chat_context) is str
        assert number_of_users > 0

        self.ws_url = ws_url
        self.chat_context = chat_context
        chat_uuid = self.ws_url.split("/")[-1]
        self.participating_users: List[User] = [User() for _ in range(number_of_users)]

        for user in self.participating_users:
            user.consumer.subscribe([chat_uuid])

        self.first_publisher: User = random.choice(self.participating_users)

        self.first_publisher.role = Role.PUBLISHER
        asyncio.run(self.connect_ws())

    @property
    def websocket(self):
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
