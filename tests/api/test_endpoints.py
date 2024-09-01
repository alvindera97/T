"""
Module for tests for application api endpoints.

Classes:
  SetUpChatEndpointTestCase
  WebSocketTestCase
"""
import os
from unittest.mock import patch

from fastapi.websockets import WebSocketDisconnect

from models import Chat
from tests.database import base


class WebSocketTestCase(base.BaseTestDatabaseTestCase):
    """
    Test case class for application web socket tests.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        patch("controller.Controller")

    def test_that_connection_to_invalid_chat_websocket_url_cannot_be_established(self) -> None:
        """
        Test that connection establishment with invalid chat web socket url cannot be established.
        The web socket connection route must pass validation checks.

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @patch("controller.controller_def.User")
    @patch("controller.Controller")
    def test_endpoint_only_takes_post_requests(self, *_) -> None:
        """
        Test that the endpoint only takes post request.
        :return: None
        """
        post_response = self.client.post("/set_up_chat/", follow_redirects=False)
        get_response = self.client.put("/set_up_chat/")
        delete_response = self.client.delete("/set_up_chat/")
        patch_response = self.client.patch("/set_up_chat/")

        self.assertTrue(post_response.status_code.__str__()[0] in {"2", "3"},  # required for OK/redirect responses.
                        f"Endpoint to set up chat is incorrect, the returned status code is: {post_response.status_code}")

        self.assertEqual(gr := get_response.status_code, 405,
                         f"Endpoint isn't supposed to accept/process get requests, the returned status code is: {gr}")
        self.assertEqual(dr := delete_response.status_code, 405,
                         f"Endpoint isn't supposed to accept/process delete requests, the returned status code is: {dr}")
        self.assertEqual(pr := patch_response.status_code, 405,
                         f"Endpoint isn't supposed to accept/process patch requests, the returned status code is: {pr}")

    @patch("controller.controller_def.User")
    @patch("controller.Controller")
    def test_endpoint_creates_new_chat_uuid_in_database_chats_table(self, *_) -> None:
        """
        Test that request to endpoint creates new unique UUID record in test database
        :return: None
        """
        previous_chat_count = self.session.query(Chat).count()
        self.client.post("/set_up_chat/")

        self.assertEqual(self.session.query(Chat).count(), previous_chat_count + 1)

    @patch("controller.controller_def.User")
    @patch("controller.Controller")
    def test_endpoint_returns_redirect_response_pointing_to_the_url_for_the_chat(self, *_) -> None:
        """
        Test that response to endpoint is a  redirect request which points to the URL for the chat.
        :return: None
        """

        post_response = self.client.post("/set_up_chat/", follow_redirects=False)

        self.assertTrue(post_response.status_code.__str__().startswith('3'))

    @patch("controller.controller_def.User")
    def test_endpoint_redirect_url_matches_that_of_the_expected_chat_url(self, *_) -> None:
        """
        Test that URL redirected to from endpoint matches expected chat url
        :return: None
        """
        with patch("api.endpoints.endpoints.Controller"):
            response = self.client.post("/set_up_chat/", follow_redirects=True)

            self.assertEqual(f'chat/{[i for i in self.session.query(Chat)][-1].uuid.__str__()}',
                             '/'.join(response.url.__str__().split("/")[-2:]))

    @patch("controller.controller_def.User")
    def test_endpoint_creates_new_application_controller_for_chat_session(self, *_) -> None:
        """
        Test that endpoint creates application controller.
        :return: None
        """
        with patch("api.endpoints.endpoints.Controller") as mock_application_controller:
            with patch("controller.controller_def.websockets"):
                response = self.client.post("/set_up_chat/", follow_redirects=True)
                mock_application_controller.assert_called_once_with(1, "ws://localhost:8000/" + "/".join(
                    response.url.__str__().split("/")[-2:]))
