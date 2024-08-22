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

from controller import Controller
from role import Role


class ApplicationControllerTestCase(unittest.TestCase):
    """
    Test case class for Application Controller
    """

    @classmethod
    def setUpClass(cls):
        cls.ws_url = "ws://localhost:8000/chat/" + os.getenv('TEST_CHAT_UUID')

    def test_controller_constructor_has_array_of_unique_users_based_on_constructor_argument(self) -> None:
        """
        Test that the controller constructor takes in kwarg for number of users and populates participating_users
        attribute with number of unique User objects is specified by the keyword argument.
        :return: None
        """
        number_of_participating_users = random.randint(2, 10)

        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            controller = Controller(number_of_participating_users, self.ws_url)

            self.assertEqual(len(set(controller.participating_users)), number_of_participating_users)
            websockets_mock.assert_called_once_with(self.ws_url)

    def test_that_controller_raises_exception_on_nonsensical_input_for_number_of_participating_users(self) -> None:
        """
        Test that the controller constructor raises an exception when non int types or an int less than one is passed
        for number of participating users.

        :return: None
        """
        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            self.assertRaises(AssertionError, lambda: Controller(0, self.ws_url))
            self.assertRaises(AssertionError, lambda: Controller(-1, self.ws_url))
            self.assertRaises(AssertionError, lambda: Controller("0", self.ws_url))

            websockets_mock.assert_not_called()

    def test_that_controller_has_first_publisher_attribute_which_must_have_role_of_publisher(self) -> None:
        """
        Test that initialised consumer has 'first_publisher' attribute which must have role of PUBLISHER
        :return: None
        """
        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            controller = Controller(2, self.ws_url)

            self.assertTrue(hasattr(controller, 'first_publisher'))
            self.assertEqual(controller.first_publisher.role, Role.PUBLISHER)

            websockets_mock.assert_called_once_with(self.ws_url)

    def test_controller_has_web_socket_url_attribute_gotten_from_constructor(self) -> None:
        """
        Test that controller has web socket url attribute and gets web socket URL as
        part of kwargs from constructor.
        :return:
        """
        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            controller = Controller(3, self.ws_url)

            self.assertTrue(hasattr(Controller, "ws_url"))
            self.assertEqual(Controller.ws_url, None)
            self.assertEqual(controller.ws_url, self.ws_url)
            websockets_mock.assert_called_once_with(self.ws_url)

    def test_controller_connects_to_chat_websocket_on_init(self) -> None:
        """
        Test that controller calls method to connect to chat web socket on init.
        :return: None
        """
        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            Controller(3, self.ws_url)

            websockets_mock.assert_called_once_with(self.ws_url)

    def test_controller_fails_to_connect_to_chat_websocket_on_invalid_url(self) -> None:
        """
        Test that controller fails to connect to the chat web socket on init when supplied with invalid url
        :return: None
        """
        self.assertRaises(websockets.InvalidURI, Controller, 2, "some-invalid-uuid")


class AsyncControllerTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.ws_url = ApplicationControllerTestCase.ws_url

    def test_controller_has_null_websocket_attribute_which_becomes_populated_on_connection(self) -> None:
        """
        Test that controller has null 'websocket' attribute before connection to chat websocket;
        after connection Controller.websocket becomes populated ideally with a websockets.WebSocketClientProtocol object.
        :return: None
        """
        self.assertIsNone(Controller._Controller__websocket)

        with patch("websockets.connect", new=AsyncMock()) as websockets_mock:
            websockets_mock.return_value = websockets.WebSocketClientProtocol()
            controller = Controller(2, self.ws_url)

            self.assertIsNotNone(controller.websocket)
            self.assertIsNotNone(controller._Controller__websocket)
            self.assertIsInstance(controller.websocket, websockets.WebSocketClientProtocol)

    def test_set_websocket_invalid_type(self) -> None:
        """
        Test that setting Controller websocket attribute to invalid type will raise Exception.
        :return:
        """
        with patch("websockets.connect", new=AsyncMock()):
            def f() -> NoReturn:
                """
                This ideally shouldn't work as trying to set Controller.websocket to anything other than
                a websockets.WebSocketClientProtocol object will cause an Exception to be raised.

                :return: This should ideally never return
                """
                Controller(2, self.ws_url).websocket = "invalid object"

            self.assertRaises(AssertionError, f)
