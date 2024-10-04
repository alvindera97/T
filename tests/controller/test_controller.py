"""
Module for tests on application controller

This module contains test cases or testing the "Controller" (otherwise called Application Controller) entity
and all related functionality.

Classes:
  ApplicationControllerTestCase
  AsyncControllerTest
"""

import os
import random
import unittest
from typing import NoReturn
from unittest.mock import patch, AsyncMock

import websockets
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from api.endpoints import app
from controller import Controller
from role import Role

test_client = TestClient(app)


class ApplicationControllerTestCase(unittest.IsolatedAsyncioTestCase):
    """
    Test case class for Application Controller
    """

    @classmethod
    def setUpClass(cls):
        cls.chat_context = "Some context"
        cls.ws_url = "ws://localhost:8000/chat/" + os.getenv("TEST_CHAT_UUID")

    async def test_controller_constructor_has_array_of_unique_users_based_on_constructor_argument(
        self,
    ) -> None:
        """
        Test that the controller constructor takes in kwarg for number of users and populates participating_users
        attribute with number of unique User objects is specified by the keyword argument.
        :return: None
        """
        with patch("websockets.connect", new=AsyncMock()):
            number_of_participating_users = random.randint(2, 10)
            controller = await Controller.initialise(
                number_of_participating_users, self.ws_url, self.chat_context
            )

            self.assertEqual(
                len(set(controller.participating_users)), number_of_participating_users
            )

    async def test_that_controller_raises_exception_on_nonsensical_input_for_number_of_participating_users(
        self,
    ) -> None:
        """
        Test that the controller constructor raises an exception when non int types or an int less than one is passed
        for number of participating users.

        :return: None
        """
        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            with self.assertRaises(
                AssertionError,
            ):
                await Controller.initialise(0, self.ws_url, self.chat_context)

            with self.assertRaises(
                AssertionError,
            ):
                await Controller.initialise(-1, self.ws_url, self.chat_context)

            with self.assertRaises(
                AssertionError,
            ):
                await Controller.initialise("0", self.ws_url, self.chat_context)

            with self.assertRaises(AssertionError):
                await Controller.initialise(2, self.ws_url, 0)

            websockets_mock.assert_not_called()

    async def test_that_controller_has_first_publisher_attribute_which_must_have_role_of_publisher(
        self,
    ) -> None:
        """
        Test that initialised consumer has 'first_publisher' attribute which must have role of PUBLISHER
        :return: None
        """
        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            controller = await Controller.initialise(2, self.ws_url, self.chat_context)

            self.assertTrue(hasattr(controller, "first_publisher"))
            self.assertEqual(controller.first_publisher.role, Role.PUBLISHER)

            websockets_mock.assert_called_once_with(self.ws_url)

    async def test_controller_has_web_socket_url_attribute_gotten_from_constructor(
        self,
    ) -> None:
        """
        Test that controller has web socket url attribute and gets web socket URL as
        part of kwargs from constructor.
        :return: None
        """
        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            controller = await Controller.initialise(3, self.ws_url, self.chat_context)

            self.assertTrue(hasattr(Controller, "ws_url"))
            self.assertEqual(Controller.ws_url, None)
            self.assertEqual(controller.ws_url, self.ws_url)
            websockets_mock.assert_called_once_with(self.ws_url)

    async def test_controller_has_string_chat_context_attribute_gotten_from_constructor(
        self,
    ) -> None:
        """
        Test that the controller has string chat context supplied by the constructor at initialisation.
        :return: None
        """

        self.assertFalse(hasattr(Controller, "chat_context"))

        with self.assertRaises(TypeError):
            await Controller.initialise(2, self.ws_url)

        with patch("websockets.connect", new=AsyncMock()):
            controller = await Controller.initialise(
                3, self.ws_url, "Some chat context"
            )
            self.assertEqual(controller.chat_context, "Some chat context")

    async def test_controller_connects_to_chat_websocket_on_init(self) -> None:
        """
        Test that controller calls method to connect to chat web socket on init.
        :return: None
        """
        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            await Controller.initialise(3, self.ws_url, self.chat_context)

            websockets_mock.assert_called_once_with(self.ws_url)

    async def test_controller_fails_to_connect_to_chat_websocket_on_invalid_url(
        self,
    ) -> None:
        """
        Test that controller fails to connect to the chat web socket on init when supplied with invalid url
        :return: None
        """
        with self.assertRaises(websockets.InvalidURI):
            await Controller.initialise(2, "some-invalid-uuid", self.chat_context)

    async def test_controller_has_null_websocket_attribute_which_becomes_populated_on_connection(
        self,
    ) -> None:
        """
        Test that controller has null 'websocket' attribute before connection to chat websocket;
        after connection Controller.websocket becomes populated ideally with a websockets.WebSocketClientProtocol object.
        :return: None
        """
        self.assertIsNone(Controller._Controller__websocket)

        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            websockets_mock.return_value = websockets.WebSocketClientProtocol()
            controller = await Controller.initialise(2, self.ws_url, self.chat_context)

            self.assertIsNotNone(controller.websocket)
            self.assertIsNotNone(controller._Controller__websocket)
            self.assertIsInstance(
                controller.websocket, websockets.WebSocketClientProtocol
            )

    async def test_set_websocket_invalid_type(self) -> None:
        """
        Test that setting Controller websocket attribute to invalid type will raise Exception.
        :return:
        """
        with patch("websockets.connect", new=AsyncMock()):

            async def f() -> NoReturn:
                """
                This ideally shouldn't work as trying to set Controller.websocket to anything other than
                a websockets.WebSocketClientProtocol object will cause an Exception to be raised.

                :return: This should ideally never return
                """
                controller = await Controller.initialise(
                    2, self.ws_url, self.chat_context
                )
                controller.websocket = "invalid object"

            with self.assertRaises(AssertionError):
                await f()

    async def test_controller_method_for_connecting_to_websocket_can_send_messages_to_websocket(
        self,
    ) -> None:
        """
        Test that Controller websocket connector can send message to websocket.
        :return:
        """
        try:
            with test_client.websocket_connect(
                "/ws/" + os.getenv("TEST_CHAT_UUID")
            ) as test_websocket_client:
                controller = await Controller.initialise(
                    2, self.ws_url, self.chat_context
                )
                await controller.connect_ws("hello world")
                data = test_websocket_client.receive_text()
                self.assertEqual(data, "hello world")
                test_websocket_client.close(reason="Done with test")

        except WebSocketDisconnect:
            pass
        except Exception as e:
            self.fail(
                f"Exception not expected from this test, raised exception is: {e}"
            )
