"""
Module for tests on application controller

This module contains test cases or testing the "Controller" (otherwise called Application Controller) entity
and all related functionality.

Classes:
  ApplicationControllerTestCase
"""
import random
import unittest
from unittest.mock import patch

from controller import Controller
from role import Role


class ApplicationControllerTestCase(unittest.TestCase):
    """
    Test case class for Application Controller
    """

    def test_controller_constructor_has_array_of_unique_users_based_on_constructor_argument(self) -> None:
        """
        Test that the controller constructor takes in kwarg for number of users and populates participating_users
        attribute with number of unique User objects is specified by the keyword argument.
        :return: None
        """
        number_of_participating_users = random.randint(2, 10)
        controller = Controller(number_of_participating_users)

        self.assertEqual(len(set(controller.participating_users)), number_of_participating_users)

    def test_that_controller_raises_exception_on_nonsensical_input_for_number_of_participating_users(self) -> None:
        """
        Test that the controller constructor raises an exception when non int types or an int less than one is passed
        for number of participating users.

        :return: None
        """
        self.assertRaises(AssertionError, lambda: Controller(0))
        self.assertRaises(AssertionError, lambda: Controller(-1))
        self.assertRaises(AssertionError, lambda: Controller("0"))

    def test_that_controller_has_first_publisher_attribute_which_must_have_role_of_publisher(self) -> None:
        """
        Test that initialised consumer has 'first_publisher' attribute which must have role of PUBLISHER
        :return: None
        """

        controller = Controller(2)
        self.assertTrue(hasattr(controller, 'first_publisher'))
        self.assertEqual(controller.first_publisher.role, Role.PUBLISHER)

    def test_controller_has_web_socket_connection_status_attribute(self) -> None:
        """
        Test that controller has attribute for status on connection to group chat web socket.
        :return: None
        """
        self.assertTrue(hasattr(Controller, "is_connected"))
        self.assertEqual(Controller.is_connected, False)

    def test_controller_has_web_socket_url_attribute_gotten_from_constructor(self) -> None:
        """
        Test that controller has web socket url attribute and gets web socket URL as
        part of kwargs from constructor.
        :return:
        """
        controller = Controller(3, "wss://localhost:8000/")

        self.assertTrue(hasattr(Controller, "ws_url"))
        self.assertEqual(Controller.ws_url, None)
        self.assertEqual(controller.ws_url, "wss://localhost:8000/")

    def test_controller_connects_to_chat_websocket_on_init(self) -> None:
        """
        Test that controller connects to chat web socket on init.
        :return: None
        """
        controller = Controller(3)
        controller_connect_ws_mock = patch("controller.Controller.connect_ws").start()

        controller_connect_ws_mock.assert_called_once()
        self.assertTrue(controller.is_connected)
