"""
Module for tests for application api endpoints.

Classes:
  SetUpChatEndpointTestCase
  WebSocketTestCase
"""
import os
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock, Mock, call

from fastapi import FastAPI
from fastapi.websockets import WebSocketDisconnect
from starlette.testclient import TestClient

from api.endpoints import app
from api.endpoints.endpoints import startup_apache_kafka, shutdown_apache_kafka, InelegantKafkaShutdownWarning
from models import Chat
from tests.database import base
from utils import exceptions


class ApplicationBackendStartupAndShutdownTest(unittest.IsolatedAsyncioTestCase):
    """
    Test case class for application backend lifecycle.
    """

    # Notice of known issues with memory stream closure bugs discussed here: https://github.com/encode/starlette/discussions/2603

    patch("subprocess.Popen",
          return_value=SimpleNamespace(returncode=0)).start()

    patch("api.endpoints.endpoints.shutdown_apache_kafka").start()

    @patch("api.endpoints.endpoints.startup_apache_kafka")
    async def test_kafka_starts_at_startup(self, mocked_startup_apache_kafka: Mock) -> None:
        """
        Test that apache kafka stated at backend startup

        :param mocked_startup_apache_kafka: Mocked function to startup apache kafka.
        :return: None
        """
        with TestClient(app):
            mocked_startup_apache_kafka.assert_called_once()

    @patch("api.endpoints.endpoints.start_apache_kafka_consumer", new_callable=AsyncMock)
    async def test_kafka_consumer_starts_at_startup(self, start_apache_kafka_consumer: Mock) -> None:
        """
        Test that apache kafka consumer is started at backend startup.

        :param start_apache_kafka_consumer: Mocked function to start apache kafka consumer
        :return: None
        """
        with TestClient(app):
            start_apache_kafka_consumer.assert_called_once()

    @patch("api.endpoints.endpoints.start_apache_kafka_producer", new_callable=AsyncMock)
    async def test_kafka_producer_for_chat_end_point_starts_at_startup(self, start_apache_kafka_producer: Mock) -> None:
        """
        Test that apache kafka producer is started at backend startup.

        :param start_apache_kafka_producer: Mocked function to start apache kafka producer
        :return: None
        """
        with TestClient(app):
            start_apache_kafka_producer.assert_called_once()

    @patch("api.endpoints.endpoints.shutdown_apache_kafka")
    @patch("api.endpoints.endpoints.close_apache_kafka_consumer", new_callable=AsyncMock)
    @patch("api.endpoints.endpoints.close_apache_kafka_producer", new_callable=AsyncMock)
    async def test_kafka_producer_and_consumer_are_closed_at_shutdown(
            self,
            close_apache_producer: Mock,
            close_apache_consumer: Mock,
            shutdown_apache: Mock) -> None:
        """
        Test that apache kafka producer and consumer is closed at close of backend.

        :param close_apache_producer: Mocked function closing the kafka producer
        :param close_apache_consumer: Mocked function closing the kafka consumer
        :param shutdown_apache: Mocked function for shutting down kafka
        :return: None
        """

        with TestClient(app):
            pass

        close_apache_consumer.assert_called_once()
        close_apache_producer.assert_called_once()

        shutdown_apache.assert_called_once()


class ApplicationBackendStartupAndShutdownFunctionsTest(unittest.IsolatedAsyncioTestCase):
    """
    Test case class for testing functions called during start up and shut down of backend.
    """

    @classmethod
    def setUpClass(cls):
        cls.mocked_subprocess_pipe: Mock = patch("subprocess.PIPE").start()

    def setUp(self):
        self.mocked_subprocess_popen: Mock = patch("subprocess.Popen",
                                                   return_value=SimpleNamespace(returncode=None)).start()

    def test_startup_apache_kafka_function_starts_apache_kafka_zookeeper(self) -> None:
        """
        Test that the function to start apache kafka starts Apache Kafka Zookeeper

        :return: None
        """
        with TestClient(app):
            expected_command = [
                os.getenv("APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH"),
                os.getenv("APACHE_KAFKA_ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH")
            ]

            self.mocked_subprocess_popen.assert_has_calls([call(expected_command, stdin=self.mocked_subprocess_pipe,
                                                                stdout=self.mocked_subprocess_pipe)])

    def test_startup_apache_kafka_function_raises_exception_on_failed_or_erroneous_startup(self) -> None:
        """
        Test that function to start apache kafka starts Apache Kafka Zookeeper raises exception if there's an erroneous start.

        :return: None
        """

        self.mocked_subprocess_popen.return_value = SimpleNamespace(returncode=1)

        self.assertRaises(subprocess.SubprocessError, startup_apache_kafka, app)

    def test_startup_apache_kafka_function_starts_apache_kafka_server_after_successful_start_of_zookeeper(self) -> None:
        """
        Test that apache kafka startup function starts up apache kafka server after successfully starting zookeeper.
        :return: None
        """

        apache_kafka_zookeeper_startup_command = [
            os.getenv("APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH")
        ]

        apache_kafka_server_startup_command = [
            os.getenv("APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("ZOOKEEPER_KAFKA_SERVER_PROPERTIES_FULL_PATH")
        ]

        # Execution without errors/interrupts

        startup_apache_kafka(app)

        self.mocked_subprocess_popen.assert_has_calls([call(apache_kafka_zookeeper_startup_command,
                                                            stdin=self.mocked_subprocess_pipe,
                                                            stdout=self.mocked_subprocess_pipe),
                                                       call(apache_kafka_server_startup_command,
                                                            stdin=self.mocked_subprocess_pipe,
                                                            stdout=self.mocked_subprocess_pipe)])

        # Execution with errors/interrupts
        self.mocked_subprocess_popen.return_value = SimpleNamespace(returncode=1)

        self.assertRaises(subprocess.SubprocessError, startup_apache_kafka, app)

        self.mocked_subprocess_popen.assert_called_with(apache_kafka_zookeeper_startup_command,
                                                        stdin=self.mocked_subprocess_pipe,
                                                        stdout=self.mocked_subprocess_pipe)  # we don't expect the call to startup kafka's server to happen here.

    def test_startup_apache_kafka_function_raises_exception_on_erroneous_startup_to_kafka_server(self) -> None:
        """
        Test that an erroneous call to start Apache Kafka server will raise an exception and thus no further start up of
        the backend server.

        :return: None
        """
        apache_kafka_zookeeper_startup_command = [
            os.getenv("APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH")
        ]

        apache_kafka_server_startup_command = [
            os.getenv("APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("ZOOKEEPER_KAFKA_SERVER_PROPERTIES_FULL_PATH")
        ]

        self.mocked_subprocess_popen.side_effect = [
            SimpleNamespace(returncode=None),
            SimpleNamespace(returncode=1)
        ]

        self.assertRaises(subprocess.SubprocessError, startup_apache_kafka, app)
        self.mocked_subprocess_popen.assert_has_calls([call(apache_kafka_zookeeper_startup_command,
                                                            stdin=self.mocked_subprocess_pipe,
                                                            stdout=self.mocked_subprocess_pipe),
                                                       call(apache_kafka_server_startup_command,
                                                            stdin=self.mocked_subprocess_pipe,
                                                            stdout=self.mocked_subprocess_pipe)])

    def test_at_successful_end_of_apache_startup_there_are_state_attributes_set_for_kafka_zookeeper_and_server_processes(
            self) -> None:
        """
        Test that after successful startup of apache kafka, there are state attributes set for kafka zookeeper and server processes
        :return: None
        """
        try:
            startup_apache_kafka(app)
        except Exception as e:
            self.fail(f"Exception raised during execution of apache kafka startup: {e}")

        self.assertTrue(hasattr(app.state, "zookeeper_subprocess"))
        self.assertTrue(hasattr(app.state, "kafka_server_subprocess"))

        self.mocked_subprocess_popen.side_effect = [
            SimpleNamespace(returncode=None),
            SimpleNamespace(returncode=-1)
        ]

        another_app = FastAPI()

        try:
            startup_apache_kafka(another_app)
        except subprocess.CalledProcessError:  # we're excepting this exception
            self.assertFalse(hasattr(another_app.state, "zookeeper_subprocess"))
            self.assertFalse(hasattr(another_app.state, "kafka_server_subprocess"))

        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    def test_shutdown_apache_kafka_raises_exception_if_existing_kafka_zookeeper_and_server_for_app_instance_is_non_existent(
            self) -> None:
        """
        Test that the function to shut down Apache Kafka raises an exception if kafka zookeeper and or server don't exist for
        the app instance upon which the shutdown was called with.

        :return: None
        """
        another_app = FastAPI()
        with self.assertRaises(exceptions.OperationNotAllowedException) as context:
            shutdown_apache_kafka(another_app)

        self.assertEqual(context.exception.__str__(),
                         "You cannot shutdown apache kafka as there's none running for this instance of the server!")

    @patch("warnings.warn")
    @patch("subprocess.Popen")
    def test_shutdown_apache_kafka_uses_subprocess_stop_if_there_is_an_error_with_using_the_official_kafka_stop_executables(
            self, mocked_subprocess_popen: Mock, *_) -> None:
        """
        Test that the function to shut down Apache Kafka uses subprocess termination
        if there was an error with the official Kafka stop executables.
        """
        another_app = FastAPI()

        apache_kafka_server_shutdown_command = [
            os.getenv("APACHE_KAFKA_SERVER_STOP_EXECUTABLE_FULL_PATH"),
        ]

        first_popen_instance = Mock()
        first_popen_instance.returncode = None
        first_popen_instance.terminate = Mock()

        second_popen_instance = Mock()
        second_popen_instance.returncode = None
        second_popen_instance.terminate = Mock()

        failing_popen_instance = Mock()
        failing_popen_instance.returncode = -1  # Third call should indicate an error

        mocked_subprocess_popen.side_effect = [
            first_popen_instance,
            second_popen_instance,
            failing_popen_instance
        ]

        # Start and then shut down Kafka
        startup_apache_kafka(another_app)
        shutdown_apache_kafka(another_app)

        mocked_subprocess_popen.assert_has_calls([
            call(apache_kafka_server_shutdown_command, stdin=self.mocked_subprocess_pipe,
                 stdout=self.mocked_subprocess_pipe),
        ])

        first_popen_instance.terminate.assert_called_once()
        second_popen_instance.terminate.assert_called_once()

    @patch("subprocess.Popen")
    def test_shutdown_apache_kafka_raises_warning_on_erroneous_official_kafka_shutdown_executable_call(self,
                                                                                                       mocked_subprocess_popen) -> None:
        """
        Test that function to shut down Apache Kafka raises warning if there was an error while executing subprocess to
        run official kafka shutdown executables.
        :return: None
        """
        another_app = FastAPI()

        first_popen_instance = Mock()
        first_popen_instance.returncode = None
        first_popen_instance.terminate = Mock()

        second_popen_instance = Mock()
        second_popen_instance.returncode = None
        second_popen_instance.terminate = Mock()

        failing_popen_instance = Mock()
        failing_popen_instance.returncode = -1  # Third call should indicate an error

        mocked_subprocess_popen.side_effect = [
            first_popen_instance,
            second_popen_instance,
            failing_popen_instance
        ]

        # Start and then shut down Kafka
        startup_apache_kafka(another_app)

        with self.assertWarns(InelegantKafkaShutdownWarning) as context:
            shutdown_apache_kafka(another_app)

        self.assertEqual(context.warning.__str__(),
                         "Kafka's Zookeeper and Server couldn't be closed via the official Kafka closure executables! A subprocess.Popen.terminate() to their subprocesses was used instead.")


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
        self.client.post("/set_up_chat/", json={"chat_context": "Hello world"})

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
            response = self.client.post("/set_up_chat/", json={"chat_context": "Hello world"},
                                        follow_redirects=True)

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
                response = self.client.post("/set_up_chat/",
                                            json={'chat_context': "Hello world"},
                                            follow_redirects=True)
                mock_application_controller.assert_called_once_with(1, "ws://localhost:8000/" + "/".join(
                    response.url.__str__().split("/")[-2:]), "Hello world")

    def test_endpoint_takes_request_json_body_of_expected_type(self) -> None:
        """
        Test that endpoint takes json request body of expected type (currently SetUpChatRequestBody)
        :return: None
        """
        with patch("api.endpoints.endpoints.Controller"):
            with patch("controller.controller_def.websockets"):
                response = self.client.post("/set_up_chat/", follow_redirects=True)
                self.assertEqual(response.status_code, 422)
