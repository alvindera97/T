"""
Module for tests for application api endpoints.

Classes:
  SetUpChatEndpointTestCase
  WebSocketTestCase
"""
import os

from fastapi.websockets import WebSocketDisconnect

from models import Chat
from tests.database import base


class WebSocketTestCase(base.BaseTestDatabaseTestCase):
    """
    Test case class for application web socket tests.
    """

    def test_that_connection_to_invalid_chat_websocket_url_cannot_be_established(self) -> None:
        """
        Test that connection establishment with invalid chat web socket url cannot be established.
        The web socket connection route must pass validation checks.

        In this instance, the validation check will be a hash set lookup.
        :return: None
        """
        url_to_connect_to = "/ws/" + os.getenv('TEST_CHAT_UUID')

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


class SetUpChatEndpointTestCase(base.BaseTestDatabaseTestCase):
    """
    Test case class for end point setting up chat.
    """

    def setUp(self):
        super().setUp()

    def test_endpoint_only_takes_post_requests(self) -> None:
        """
        Test that the endpoint only takes post request.
        :return: None
        """
        post_response = self.client.post("/set_up_chat/")
        get_response = self.client.put("/set_up_chat/")
        delete_response = self.client.delete("/set_up_chat/")
        patch_response = self.client.patch("/set_up_chat/")

        self.assertEqual(post_response.status_code.__str__()[0], "2",  # required for OK responses.
                         f"Endpoint to set up chat is incorrect, the returned status code is: {post_response.status_code}")

        self.assertEqual(gr := get_response.status_code, 405,
                         f"Endpoint isn't supposed to accept/process get requests, the returned status code is: {gr}")
        self.assertEqual(dr := delete_response.status_code, 405,
                         f"Endpoint isn't supposed to accept/process delete requests, the returned status code is: {dr}")
        self.assertEqual(pr := patch_response.status_code, 405,
                         f"Endpoint isn't supposed to accept/process patch requests, the returned status code is: {pr}")

    def test_endpoint_creates_new_chat_uuid_in_database_chats_table(self) -> None:
        """
        Test that request to endpoint creates new unique UUID record in test database
        :return: None
        """
        previous_chat_count = self.session.query(Chat).count()

        response = self.client.post("/set_up_chat/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.session.query(Chat).count(), previous_chat_count + 1)
