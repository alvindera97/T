"""
Module for tests for application api endpoints.

Classes:
  SetUpChatEndpointTestCase
  WebSocketTestCase
"""

import os
import unittest
import uuid
import warnings
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock, Mock

from fastapi import FastAPI
from fastapi.websockets import WebSocketDisconnect
from starlette.testclient import TestClient

from api.endpoints import app
from api.endpoints.endpoints import (
    InelegantKafkaShutdownWarning,
    start_apache_kafka_producer,
    MultipleKafkaProducerStartWarning,
    close_apache_kafka_producer,
)
from models import Chat
from tests.database import base
from utils import exceptions

timedotsleep_patcher = None


def setUpModule():
    """
    Function containing executions before tests in module are run.
    :return:
    """
    global timedotsleep_patcher, eventlet_timeout_patcher

    timedotsleep_patcher = patch("time.sleep")

    patch("builtins.print").start()

    timedotsleep_patcher.start()


def tearDownModule():
    """
    Function containing executions after tests in module are ran.
    :return:
    """
    global timedotsleep_patcher

    if isinstance(timedotsleep_patcher, Mock):
        timedotsleep_patcher.stop()


class ApplicationBackendStartupAndShutdownTest(unittest.IsolatedAsyncioTestCase):
    """
    Test case class for application backend lifecycle.
    """

    def setUp(self):
        patch(
            "subprocess.Popen",
            return_value=SimpleNamespace(
                returncode=None, stdout=0, stderr=0, kill=lambda: None
            ),
        ).start()

        patch(
            "select.select",
            return_value=(
                [
                    SimpleNamespace(readline=lambda: "first"),
                    SimpleNamespace(
                        readline=lambda: "binding to port 0.0.0.0/0.0.0.0:2181"
                    ),
                    SimpleNamespace(
                        readline=lambda: "started (kafka.server.KafkaServer)"
                    ),
                ],
                ["second"],
                ["third"],
            ),
        ).start()

    @patch(
        "api.endpoints.endpoints.start_apache_kafka_producer", new_callable=AsyncMock
    )
    async def test_kafka_producer_for_chat_end_point_starts_at_startup(
        self, mocked_start_apache_kafka_producer: Mock
    ) -> None:
        """
        Test that apache kafka producer is started at backend startup.

        :param mocked_start_apache_kafka_producer: Mocked function to start apache kafka producer
        :return: None
        """
        with TestClient(app):
            mocked_start_apache_kafka_producer.assert_called_once()


# noinspection PyPep8Naming
class ApplicationBackendStartupAndShutdownFunctionsTest(
    unittest.IsolatedAsyncioTestCase
):
    """
    Test case class for testing functions called during start up and shut down of backend.
    """

    @classmethod
    def setUpClass(cls):
        cls.mocked_subprocess_pipe: Mock = patch("subprocess.PIPE").start()

        warnings.simplefilter("ignore", category=InelegantKafkaShutdownWarning)
        warnings.simplefilter("ignore", category=MultipleKafkaProducerStartWarning)

    def setUp(self):
        self.ModifiedAsyncMock = AsyncMock()
        self.ModifiedAsyncMock.start = AsyncMock()
        self.ModifiedAsyncMock.stop = AsyncMock()

        self.mocked_subprocess_popen: Mock = patch(
            "subprocess.Popen",
            return_value=SimpleNamespace(
                returncode=None, stderr=0, stdout=0, kill=lambda: None
            ),
        ).start()

        self.mocked_AIOKafkaProducer = patch(
            "api.endpoints.endpoints.AIOKafkaProducer",
            return_value=self.ModifiedAsyncMock,
        ).start()

        self.mocked_select_select = patch(
            "select.select",
            return_value=(
                [
                    SimpleNamespace(readline=lambda: "first"),
                    SimpleNamespace(
                        readline=lambda: "binding to port 0.0.0.0/0.0.0.0:2181"
                    ),
                    SimpleNamespace(
                        readline=lambda: "started (kafka.server.KafkaServer)"
                    ),
                ],
                ["second"],
                ["third"],
            ),
        ).start()

    def tearDown(self):
        app.state._state.clear()

        self.mocked_subprocess_popen.stop()
        self.mocked_subprocess_pipe.stop()
        self.mocked_select_select.stop()

    @patch("api.endpoints.endpoints.start_apache_kafka_producer")
    def test_start_apache_kafka_producer_takes_a_fastapi_object_argument(
        self, mocked_start_apache_kafka_producer: Mock
    ) -> None:
        """
        Test that function to start apache kafka producer takes FastAPI app instance argument.

        :param mocked_start_apache_kafka_producer: Mocked start_apache_kafka_producer() object.
        :return: None
        """

        with TestClient(app):
            mocked_start_apache_kafka_producer.assert_called_once_with(app)
            app.state.kafka_producer = self.mocked_AIOKafkaProducer()

    def test_start_apache_kafka_producer_sets_fastapi_app_kafka_producer_attribute(
        self,
    ) -> None:
        """
        Test that function to start apache kafka producer sets the fastapi state kafka_producer attribute.

        :return: None
        """
        with TestClient(app):
            self.assertIsNotNone(app.state.kafka_producer)

    async def test_start_apache_kafka_producer_does_not_recreate_another_producer_on_the_same_instance_of_fastapi(
        self,
    ) -> None:
        """
        Test that function to start apache kafka producer does not create more than one for a single fastapi app instance.

        :return: None
        """

        with TestClient(app):
            with self.assertWarns(MultipleKafkaProducerStartWarning) as context:
                await start_apache_kafka_producer(app)

            expected_warning_text = f"There's an existing kafka producer for this app instance: {hex(id(app))}"

            if context.warning.__str__() != expected_warning_text:
                self.fail(
                    f"Improper handling of repeated start of kafka producer for app instance\nexpected: {expected_warning_text}\nactual: {context.warning.__str__()}"
                )

            self.mocked_AIOKafkaProducer.assert_called_once()

    async def test_start_apache_kafka_producer_starts_AIOKafkaProducer_with_expected_argument_for_boostrap_servers(
        self,
    ) -> None:
        """
        Test that function to start apache kafka producer starts AIOKafkaProducer with expected values.
        :return: None
        """

        with TestClient(app):
            self.mocked_AIOKafkaProducer.assert_called_once_with(
                bootstrap_servers=f'{os.getenv("APACHE_KAFKA_BOOTSTRAP_SERVER_HOST")}:{os.getenv("APACHE_KAFKA_BOOTSTRAP_SERVER_PORT")}'
            )

    def test_start_apache_kafka_producer_starts_the_kafka_producer(self) -> None:
        """
        Test that function to start apache kafka producer calls .start() on the AIOKafkaProducer object.
        :return: None
        """
        with TestClient(app):
            self.mocked_AIOKafkaProducer().start.assert_called_once()

    async def test_close_apache_kafka_producer_calls_close_on_the_server_AIOKafkaProducer_object(
        self,
    ) -> None:
        """
        Test that function to close server Apache Kafka Producer (in this case AIOKafkaProducer) closes the server producer
        AIOKafkaProducer object.

        :return: None
        """

        another_app = FastAPI()

        # then start kafka producer
        await start_apache_kafka_producer(another_app)

        # then stop kafka producer
        await close_apache_kafka_producer(another_app)

        self.mocked_AIOKafkaProducer().stop.assert_called_once()

    async def test_close_apache_kafka_producer_triggers_warning_when_supplied_fastapi_application_instance_has_no_kafka_producer_state_attribute(
        self,
    ):
        """
        Test that functon to close server Apache Kafka Producer triggers a warning in the case that there is no kafka producer
        state attribute on the passed fastapi application argument.
        :return: None
        """
        another_app = FastAPI()
        with self.assertWarns(InelegantKafkaShutdownWarning) as context:
            await close_apache_kafka_producer(another_app)

        self.assertEqual(
            context.warning.__str__(),
            "You cannot shutdown apache kafka producer as there's none [recorded] running for this instance of the server!",
        )

        self.mocked_AIOKafkaProducer().stop.assert_not_called()


class WebSocketTestCase(base.BaseTestDatabaseTestCase):
    """
    Test case class for application web socket tests.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        patch("controller.Controller")

    def test_that_connection_to_invalid_chat_websocket_url_cannot_be_established(
        self,
    ) -> None:
        """
        Test that connection establishment with invalid chat web socket url cannot be established.
        The web socket connection route must pass validation checks.

        :return: None
        """
        url_to_connect_to = "/ws/" + os.getenv("TEST_CHAT_URL")

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
                f"Web socket connection to {url_to_connect_to} isn't supposed to raise an exception, exception raised is: {e} "
            )


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

        self.assertTrue(
            post_response.status_code.__str__()[0]
            in {"2", "3"},  # required for OK/redirect responses.
            f"Endpoint to set up chat is incorrect, the returned status code is: {post_response.status_code}",
        )

        self.assertEqual(
            gr := get_response.status_code,
            405,
            f"Endpoint isn't supposed to accept/process get requests, the returned status code is: {gr}",
        )
        self.assertEqual(
            dr := delete_response.status_code,
            405,
            f"Endpoint isn't supposed to accept/process delete requests, the returned status code is: {dr}",
        )
        self.assertEqual(
            pr := patch_response.status_code,
            405,
            f"Endpoint isn't supposed to accept/process patch requests, the returned status code is: {pr}",
        )

    @patch("controller.controller_def.User")
    @patch("controller.Controller.initialise")
    def test_endpoint_creates_new_chat_uuid_in_database_chats_table(self, *_) -> None:
        """
        Test that request to endpoint creates new unique UUID record in test database
        :return: None
        """
        previous_chat_count = self.session.query(Chat).count()
        self.client.post("/set_up_chat/", json={"chat_context": "Hello world"})

        self.assertEqual(self.session.query(Chat).count(), previous_chat_count + 1)

    @patch("controller.controller_def.User")
    @patch("controller.Controller")
    def test_endpoint_returns_redirect_response_pointing_to_the_url_for_the_chat(
        self, *_
    ) -> None:
        """
        Test that response to endpoint is a  redirect request which points to the URL for the chat.
        :return: None
        """

        post_response = self.client.post("/set_up_chat/", follow_redirects=False)

        self.assertTrue(post_response.status_code.__str__().startswith("3"))

    @patch("api.endpoints.endpoints.utility_functions.create_apache_kafka_topic")
    @patch("controller.controller_def.User")
    def test_endpoint_redirect_url_matches_that_of_the_expected_chat_url(
        self, *_
    ) -> None:
        """
        Test that URL redirected to from endpoint matches expected chat url
        :return: None
        """
        with patch(
            "api.endpoints.endpoints.Controller.initialise", new_callable=AsyncMock
        ):
            response = self.client.post(
                "/set_up_chat/",
                json={"chat_context": "Hello world"},
                follow_redirects=True,
            )

            self.assertEqual(
                f"chat/{[i for i in self.session.query(Chat)][-1].uuid.__str__()}",
                "/".join(response.url.__str__().split("/")[-2:]),
            )

    @patch("controller.controller_def.User")
    @patch("api.endpoints.endpoints.utility_functions.create_apache_kafka_topic")
    def test_endpoint_creates_new_application_controller_for_chat_session(
        self, *_
    ) -> None:
        """
        Test that endpoint creates application controller.
        :return: None
        """
        with patch(
            "api.endpoints.endpoints.Controller.initialise", new_callable=AsyncMock
        ) as mock_application_controller_initialise:
            with patch("controller.controller_def.websockets"):
                response = self.client.post(
                    "/set_up_chat/",
                    json={"chat_context": "Hello world"},
                    follow_redirects=True,
                )
                mock_application_controller_initialise.assert_called_once_with(
                    1,
                    "ws://localhost:8000/"
                    + "/".join(response.url.__str__().split("/")[-2:]),
                    "Hello world",
                )

    @patch("api.endpoints.endpoints.Controller")
    def test_endpoint_does_not_create_new_application_controller_if_there_is_a_failure_to_create_kafka_topic(
        self, mocked_application_controller: Mock
    ) -> None:
        """
        Test that endpoint does not create application controller in the event that creation of kafka topic was
        unsuccessful.
        :return: None
        """
        test_chat_uuid = uuid.uuid4().__str__()
        with patch(
            "api.endpoints.endpoints.utility_functions.create_apache_kafka_topic",
            side_effect=[ValueError],
        ) as mocked_create_apache_kafka_topic:
            with patch(
                "api.endpoints.endpoints.utility_functions.add_new_chat",
                return_value=test_chat_uuid,
            ):
                with patch("api.endpoints.endpoints.app") as mocked_fastapi_app:
                    self.client.post(
                        "/set_up_chat/",
                        json={"chat_context": "Hello world"},
                        follow_redirects=True,
                    )
                    mocked_create_apache_kafka_topic.assert_called_once_with(
                        test_chat_uuid, mocked_fastapi_app
                    )
                    mocked_application_controller.assert_not_called()

    def test_endpoint_takes_request_json_body_of_expected_type(self) -> None:
        """
        Test that endpoint takes json request body of expected type (currently SetUpChatRequestBody)
        :return: None
        """
        with patch("api.endpoints.endpoints.Controller"):
            with patch("controller.controller_def.websockets"):
                response = self.client.post("/set_up_chat/", follow_redirects=True)
                self.assertEqual(response.status_code, 422)

    def test_endpoint_creates_kafka_topic_for_the_chat_before_returning_response_on_successful_function_call(
        self,
    ) -> None:
        """
        Test that endpoint calls function to create kafka topic before returning a response.
        :return: None
        """
        test_chat_uuid = uuid.uuid4().__str__()
        with patch(
            "api.endpoints.endpoints.Controller.initialise", new_callable=AsyncMock
        ):
            with patch("api.endpoints.endpoints.app") as mocked_fastapi_app:
                with patch(
                    "api.endpoints.endpoints.utility_functions.create_apache_kafka_topic"
                ) as mocked_create_apache_kafka_topic:
                    with patch(
                        "api.endpoints.endpoints.utility_functions.add_new_chat",
                        return_value=test_chat_uuid,
                    ):
                        self.client.post(
                            "/set_up_chat/",
                            json={"chat_context": "Hello world"},
                            follow_redirects=True,
                        )
                        mocked_create_apache_kafka_topic.assert_called_once_with(
                            test_chat_uuid, mocked_fastapi_app
                        )

    def test_endpoint_returns_server_error_on_exception_from_function_to_create_kafka_topic(
        self,
    ) -> None:
        """
        Test that endpoints returns with server error in the event that there is a failure (characterised by an exception
        while creating the kafka topic).
        :return: None
        """
        test_chat_uuid = uuid.uuid4().__str__()
        with patch("api.endpoints.endpoints.Controller"):
            with patch("api.endpoints.endpoints.app") as mocked_fastapi_app:
                with patch(
                    "api.endpoints.endpoints.utility_functions.create_apache_kafka_topic",
                    side_effect=[ValueError],
                ) as mocked_create_apache_kafka_topic:
                    with patch(
                        "api.endpoints.endpoints.utility_functions.add_new_chat",
                        return_value=test_chat_uuid,
                    ):
                        response = self.client.post(
                            "/set_up_chat/",
                            json={"chat_context": "Hello world"},
                            follow_redirects=True,
                        )
                        mocked_create_apache_kafka_topic.assert_called_once_with(
                            test_chat_uuid, mocked_fastapi_app
                        )

                        self.assertEqual(response.status_code, 500)
                        self.assertEqual(
                            '{"detail":"An internal server error occurred at the final stages of setting up your new chat."}',
                            response.text,
                        )
