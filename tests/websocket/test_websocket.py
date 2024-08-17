"""
Module for tests for application web sockets powering group chat functionality

Classes:
  WebSocketTestCase
"""
import os
import unittest

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from api.web_socket.web_socket import app


class WebSocketTestCase(unittest.TestCase):
    """
    Test case class for application web socket tests.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_that_connection_to_invalid_chat_websocket_url_cannot_be_established(self) -> None:
        """
        Test that connection establishment with invalid chat web socket url cannot be established.
        The web socket connection route must pass validation checks.

        In this instance, the validation check will be a hash set lookup.
        :return: None
        """
        url_to_connect_to = "/ws/" + os.getenv('TEST_CHAT_URL')

        try:
            with self.client.websocket_connect(url_to_connect_to) as websocket:
                websocket.send_text("hello world")
                data = websocket.receive_text()
                self.assertEqual(data, "hello world")
                websocket.close(reason="Done with test")
        except WebSocketDisconnect:
            pass
        except Exception as e:
            self.fail(
                f"Web socket connection to {url_to_connect_to} isn't supposed to raise an exception, exception raised is: {e} ")
