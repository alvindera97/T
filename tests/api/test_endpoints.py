"""
Module for tests for application api endpoints.

Classes:
  SetUpChatEndpointTestCase
  WebSocketTestCase
"""

import os
import random
import subprocess
import unittest
import uuid
import warnings
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock, Mock, call

import eventlet
from fastapi import FastAPI
from fastapi.websockets import WebSocketDisconnect
from starlette.testclient import TestClient

from api.endpoints import app
from api.endpoints.endpoints import (
    startup_apache_kafka,
    shutdown_apache_kafka,
    InelegantKafkaShutdownWarning,
    start_apache_kafka_producer,
    MultipleKafkaProducerStartWarning,
    close_apache_kafka_producer,
)
from models import Chat
from tests.database import base
from utils import exceptions

timedotsleep_patcher = eventlet_timeout_patcher = None


def setUpModule():
    """
    Function containing executions before tests in module are run.
    :return:
    """
    global timedotsleep_patcher, eventlet_timeout_patcher

    timedotsleep_patcher = patch("time.sleep")
    eventlet_timeout_patcher = patch("api.endpoints.endpoints.eventlet.Timeout")

    patch("builtins.print").start()

    eventlet_timeout_patcher.start()
    timedotsleep_patcher.start()


def tearDownModule():
    """
    Function containing executions after tests in module are ran.
    :return:
    """
    global timedotsleep_patcher, eventlet_timeout_patcher

    if isinstance(timedotsleep_patcher, Mock):
        timedotsleep_patcher.stop()

    if isinstance(eventlet_timeout_patcher, Mock):
        eventlet_timeout_patcher.stop()


class ApplicationBackendStartupAndShutdownTest(unittest.IsolatedAsyncioTestCase):
    """
    Test case class for application backend lifecycle.
    """

    # Notice of known issues with memory stream closure bugs discussed here: https://github.com/encode/starlette/discussions/2603

    def setUp(self):
        patch(
            "subprocess.Popen",
            return_value=SimpleNamespace(
                returncode=None, stdout=0, stderr=0, kill=lambda: None
            ),
        ).start()

        patch("api.endpoints.endpoints.shutdown_apache_kafka").start()
        patch(
            "api.endpoints.endpoints.eventlet.Timeout",
            side_effect=[True, False, True, False],
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

    @patch("api.endpoints.endpoints.startup_apache_kafka")
    async def test_kafka_starts_at_startup(
        self, mocked_startup_apache_kafka: Mock
    ) -> None:
        """
        Test that apache kafka stated at backend startup

        :param mocked_startup_apache_kafka: Mocked function to startup apache kafka.
        :return: None
        """
        with TestClient(app):
            mocked_startup_apache_kafka.assert_called_once()

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

    @patch("api.endpoints.endpoints.shutdown_apache_kafka")
    @patch(
        "api.endpoints.endpoints.close_apache_kafka_producer", new_callable=AsyncMock
    )
    async def test_kafka_producer_and_consumer_are_closed_at_shutdown(
        self, close_apache_producer: Mock, shutdown_apache: Mock
    ) -> None:
        """
        Test that apache kafka producer and consumer is closed at close of backend.

        :param close_apache_producer: Mocked function closing the kafka producer
        :param shutdown_apache: Mocked function for shutting down kafka
        :return: None
        """

        with TestClient(app):
            pass

        close_apache_producer.assert_called_once()

        shutdown_apache.assert_called_once()


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

        self.mocked_eventlet_timeout = patch(
            "api.endpoints.endpoints.eventlet.Timeout", side_effect=[True, True]
        ).start()

    def tearDown(self):
        app.state._state.clear()

        self.mocked_subprocess_popen.stop()
        self.mocked_subprocess_pipe.stop()
        self.mocked_select_select.stop()

    def test_startup_apache_kafka_function_starts_apache_kafka_zookeeper(self) -> None:
        """
        Test that the function to start apache kafka starts Apache Kafka Zookeeper

        :return: None
        """
        with TestClient(app):
            expected_command = [
                os.getenv("APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH"),
                os.getenv(
                    "APACHE_KAFKA_ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH"
                ),
            ]

            self.mocked_subprocess_popen.assert_has_calls(
                [
                    call(
                        expected_command,
                        stderr=self.mocked_subprocess_pipe,
                        stdout=self.mocked_subprocess_pipe,
                        text=True,
                    )
                ]
            )

    def test_startup_apache_kafka_function_prints_contents_of_startup_output_to_terminal_during_execution(
        self,
    ) -> None:
        """
        Test that the function to start apache kafka prints the contents of the subprocess call to the terminal running
        the initiating [parent] program.
        :return: None
        """

        another_app = FastAPI()

        with patch("builtins.print") as mocked_print_function:
            startup_apache_kafka(another_app)

            self.mocked_select_select.assert_has_calls([call([0, 0], [], [], 0.1)])

            ready_to_read = self.mocked_select_select.return_value[0]
            mocked_print_function.assert_has_calls(
                [call(ready_to_read[0].readline().strip())]
            )

    def test_startup_apache_kafka_function_only_continues_to_start_kafka_server_after_zookeeper_subprocess_prints_expected_start_text(
        self,
    ) -> None:
        """
        Test that the function to start apache kafka goes on to start the apache kafka server only after the zookeeper subprocess
        output has printed out the expected text for a successful zookeeper server start.

        :return: None
        """

        apache_kafka_zookeeper_startup_command = [
            os.getenv("APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH"),
        ]

        another_app = FastAPI()
        text_from_apache_kafka_zookeeper_indicating_successful_start = (
            "binding to port 0.0.0.0/0.0.0.0:2181"
        )

        with patch("builtins.print") as mocked_print_function:
            startup_apache_kafka(another_app)

            mocked_print_function.assert_has_calls(
                [
                    call(text_from_apache_kafka_zookeeper_indicating_successful_start),
                    call("\nSUCCESSFULLY STARTED APACHE KAFKA ZOOKEEPER\n"),
                ]
            )

            self.mocked_subprocess_popen.assert_has_calls(
                [
                    call(
                        apache_kafka_zookeeper_startup_command,
                        stderr=self.mocked_subprocess_pipe,
                        stdout=self.mocked_subprocess_pipe,
                        text=True,
                    )
                ]
            )

    @patch(
        "api.endpoints.endpoints.eventlet.Timeout",
        side_effect=[True, True, True, True, eventlet.timeout.Timeout],
    )
    def test_start_apache_kafka_function_raises_exception_when_zookeeper_does_not_start_within_set_timeout(
        self, mocked_eventlet_timeout: Mock
    ) -> None:
        """
        Test that the function to start apache kafka raises exception when apache kafka zookeeper server doesn't start
        after the set timeout period (and thus there is no attempt to start up the apache kafka server.

        :return: None
        """
        apache_kafka_server_startup_command = [
            os.getenv("APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_SERVER_PROPERTIES_FULL_PATH"),
        ]

        another_app = FastAPI()
        text_from_apache_kafka_zookeeper_indicating_successful_start = (
            "binding to port 0.0.0.0/0.0.0.0:2181"
        )

        with patch("builtins.print") as mocked_print_function:
            self.mocked_select_select = patch(
                "select.select",
                return_value=(
                    [
                        SimpleNamespace(readline=lambda: "first"),
                    ],
                    ["second"],
                    ["third"],
                ),
            ).start()

            self.assertRaises(
                eventlet.timeout.Timeout, startup_apache_kafka, another_app
            )

            mocked_eventlet_timeout.assert_called_with(
                int(os.getenv("APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS"))
            )

            self.assertNotIn(
                call(text_from_apache_kafka_zookeeper_indicating_successful_start),
                mocked_print_function.mock_calls,
            )
            self.assertNotIn(
                call(
                    apache_kafka_server_startup_command,
                    stderr=self.mocked_subprocess_pipe,
                    stdout=self.mocked_subprocess_pipe,
                ),
                self.mocked_subprocess_popen.mocked_calls,
            )

    def test_startup_apache_kafka_function_raises_exception_on_failed_or_erroneous_startup(
        self,
    ) -> None:
        """
        Test that function to start apache kafka starts Apache Kafka Zookeeper raises exception if there's an erroneous start.

        :return: None
        """

        self.mocked_subprocess_popen.return_value = SimpleNamespace(
            returncode=1, stderr=0, stdout=0
        )

        self.assertRaises(subprocess.SubprocessError, startup_apache_kafka, app)

    @patch(
        "api.endpoints.endpoints.eventlet.Timeout",
        side_effect=[True, False, True, False],
    )
    def test_startup_apache_kafka_function_starts_apache_kafka_server_after_successful_start_of_zookeeper(
        self, *_
    ) -> None:
        """
        Test that apache kafka startup function starts up apache kafka server after successfully starting zookeeper.
        :return: None
        """

        apache_kafka_zookeeper_startup_command = [
            os.getenv("APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH"),
        ]

        apache_kafka_server_startup_command = [
            os.getenv("APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_SERVER_PROPERTIES_FULL_PATH"),
        ]

        # Execution without errors/interrupts

        startup_apache_kafka(app)

        self.mocked_subprocess_popen.assert_has_calls(
            [
                call(
                    apache_kafka_zookeeper_startup_command,
                    stderr=self.mocked_subprocess_pipe,
                    stdout=self.mocked_subprocess_pipe,
                    text=True,
                ),
                call(
                    apache_kafka_server_startup_command,
                    stderr=self.mocked_subprocess_pipe,
                    stdout=self.mocked_subprocess_pipe,
                    text=True,
                ),
            ]
        )

        # Execution with errors/interrupts
        self.mocked_subprocess_popen.return_value = SimpleNamespace(
            returncode=1, stdout=0, stderr=0
        )

        self.assertRaises(subprocess.SubprocessError, startup_apache_kafka, app)

        self.mocked_subprocess_popen.assert_called_with(
            apache_kafka_zookeeper_startup_command,
            stderr=self.mocked_subprocess_pipe,
            stdout=self.mocked_subprocess_pipe,
            text=True,
        )  # we don't expect the call to startup kafka's server to happen here.

    def test_startup_apache_kafka_function_raises_exception_on_erroneous_startup_to_kafka_server(
        self,
    ) -> None:
        """
        Test that an erroneous call to start Apache Kafka server will raise an exception and thus no further start up of
        the backend server.

        :return: None
        """
        apache_kafka_zookeeper_startup_command = [
            os.getenv("APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH"),
        ]

        apache_kafka_server_startup_command = [
            os.getenv("APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_SERVER_PROPERTIES_FULL_PATH"),
        ]

        self.mocked_subprocess_popen.side_effect = [
            SimpleNamespace(returncode=None, stdout=0, stderr=0, kill=lambda: None),
            SimpleNamespace(returncode=1, stdout=0, stderr=0, kill=lambda: None),
        ]

        if random.choice([True, False]):
            self.mocked_select_select = patch(
                "select.select",
                return_value=(
                    [
                        SimpleNamespace(readline=lambda: "first"),
                        SimpleNamespace(
                            readline=lambda: random.choice(
                                [
                                    "Exiting Kafka",
                                    "Failed to acquire lock on file .lock",
                                ]
                            )
                        ),
                    ],
                    ["second"],
                    ["third"],
                ),
            ).start()

            self.mocked_eventlet_timeout = patch(
                "api.endpoints.endpoints.eventlet.Timeout",
                side_effect=int(os.getenv("APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS"))
                * 2
                * [True],
            ).start()

        self.assertRaises(subprocess.SubprocessError, startup_apache_kafka, app)
        self.mocked_subprocess_popen.assert_has_calls(
            [
                call(
                    apache_kafka_zookeeper_startup_command,
                    stderr=self.mocked_subprocess_pipe,
                    stdout=self.mocked_subprocess_pipe,
                    text=True,
                ),
                call(
                    apache_kafka_server_startup_command,
                    stderr=self.mocked_subprocess_pipe,
                    stdout=self.mocked_subprocess_pipe,
                    text=True,
                ),
            ]
        )

    @patch(
        "api.endpoints.endpoints.eventlet.Timeout",
        side_effect=[True, True, True, True, False],
    )
    def test_startup_apache_kafka_function_prints_contents_of_apache_kafka_server_start_after_starting_kafka_zookeeper(
        self, mocked_eventlet_timeout: Mock
    ) -> None:
        """
        Test that function to start apache kafka prints contents of the apache kafka server process to terminal after
        successful start of apache kafka zookeeper.
        :return: None
        """
        apache_kafka_server_startup_command = [
            os.getenv("APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_SERVER_PROPERTIES_FULL_PATH"),
        ]

        another_app = FastAPI()
        text_from_apache_kafka_server_start_indicating_successful_start = (
            "started (kafka.server.KafkaServer)"
        )

        with patch("builtins.print") as mocked_print_function:
            startup_apache_kafka(another_app)

            self.mocked_subprocess_popen.assert_has_calls(
                [
                    call(
                        apache_kafka_server_startup_command,
                        stderr=self.mocked_subprocess_pipe,
                        stdout=self.mocked_subprocess_pipe,
                        text=True,
                    )
                ]
            )

            mocked_eventlet_timeout.assert_called_with(
                int(os.getenv("APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS"))
            )

            self.mocked_select_select.assert_has_calls([call([0, 0], [], [], 0.1)])

            mocked_print_function.assert_has_calls(
                [
                    call(
                        text_from_apache_kafka_server_start_indicating_successful_start
                    ),
                    call("\nSUCCESSFULLY STARTED APACHE KAFKA SERVER\n"),
                ]
            )

    @patch(
        "api.endpoints.endpoints.eventlet.Timeout",
        side_effect=[True, True, True, eventlet.timeout.Timeout],
    )
    def test_startup_apache_kafka_function_raises_exception_on_apache_kafka_server_start_timeout(
        self, mocked_eventlet_timeout: Mock
    ) -> None:
        """
        Test that function to start apache kafka raises exception if there is a timeout for the kafka server to start.
        :return: None
        """
        apache_kafka_server_startup_command = [
            os.getenv("APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_SERVER_PROPERTIES_FULL_PATH"),
        ]

        another_app = FastAPI()
        text_from_apache_kafka_server_start_indicating_successful_start = (
            "started (kafka.server.KafkaServer)"
        )

        with patch("builtins.print") as mocked_print_function:
            self.mocked_select_select = patch(
                "select.select",
                return_value=(
                    [
                        SimpleNamespace(readline=lambda: "first"),
                        SimpleNamespace(
                            readline=lambda: "binding to port 0.0.0.0/0.0.0.0:2181"
                        ),
                    ],
                    ["second"],
                    ["third"],
                ),
            ).start()

            self.assertRaises(
                eventlet.timeout.Timeout, startup_apache_kafka, another_app
            )

            mocked_eventlet_timeout.assert_called_with(
                int(os.getenv("APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS"))
            )

            self.mocked_subprocess_popen.assert_called_with(
                apache_kafka_server_startup_command,
                stdout=self.mocked_subprocess_pipe,
                stderr=self.mocked_subprocess_pipe,
                text=True,
            )

            self.assertNotIn(
                call(text_from_apache_kafka_server_start_indicating_successful_start),
                mocked_print_function.mock_calls,
            )

            self.assertFalse(hasattr(another_app.state, "zookeeper_subprocess"))
            self.assertFalse(hasattr(another_app.state, "kafka_server_subprocess"))

    @patch("api.endpoints.endpoints.eventlet.Timeout", side_effect=[True, True])
    def test_startup_apache_kafka_raises_exception_on_failed_apache_kafka_server_startup(
        self, mocked_eventlet_timeout: Mock
    ) -> None:
        """
        Test that function to start apache kafka raises exception if during the startup of apache kafka server there
        was a startup failure.
        :return: None
        """

        apache_kafka_server_startup_command = [
            os.getenv("APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH"),
            os.getenv("APACHE_KAFKA_SERVER_PROPERTIES_FULL_PATH"),
        ]

        another_app = FastAPI()
        text_from_apache_kafka_server_start_indicating_successful_start = (
            "started (kafka.server.KafkaServer)"
        )

        with patch("builtins.print") as mocked_print_function:
            self.mocked_select_select = patch(
                "select.select",
                return_value=(
                    [
                        SimpleNamespace(readline=lambda: "first"),
                        SimpleNamespace(
                            readline=lambda: "binding to port 0.0.0.0/0.0.0.0:2181"
                        ),
                        SimpleNamespace(
                            readline=lambda: random.choice(
                                [
                                    "Failed to acquire lock on file .lock",
                                    "shutting down (kafka.server.KafkaServer)",
                                ]
                            )
                        ),
                    ],
                    ["second"],
                    ["third"],
                ),
            ).start()

            self.assertRaises(
                subprocess.CalledProcessError, startup_apache_kafka, another_app
            )

            mocked_eventlet_timeout.assert_called_with(
                int(os.getenv("APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS"))
            )

            self.mocked_subprocess_popen.assert_called_with(
                apache_kafka_server_startup_command,
                stdout=self.mocked_subprocess_pipe,
                stderr=self.mocked_subprocess_pipe,
                text=True,
            )

            mocked_print_function.assert_has_calls(
                [call("\nFAILED TO STARTUP APACHE KAFKA SERVER\n")]
            )

            self.assertNotIn(
                call(text_from_apache_kafka_server_start_indicating_successful_start),
                mocked_print_function.mock_calls,
            )

            self.assertFalse(hasattr(another_app.state, "zookeeper_subprocess"))
            self.assertFalse(hasattr(another_app.state, "kafka_server_subprocess"))

    @patch(
        "api.endpoints.endpoints.eventlet.Timeout",
        side_effect=[True, False, True, False],
    )
    def test_at_successful_end_of_apache_startup_there_are_state_attributes_set_for_kafka_zookeeper_and_server_processes(
        self, *_
    ) -> None:
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
            SimpleNamespace(returncode=None, stdout=0, stderr=0),
            SimpleNamespace(returncode=-1, stdout=0, stderr=0),
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
        self,
    ) -> None:
        """
        Test that the function to shut down Apache Kafka raises an exception if kafka zookeeper and or server don't exist for
        the app instance upon which the shutdown was called with.

        :return: None
        """
        another_app = FastAPI()
        with self.assertRaises(exceptions.OperationNotAllowedException) as context:
            shutdown_apache_kafka(another_app)

        self.assertEqual(
            context.exception.__str__(),
            "You cannot shutdown apache kafka as there's none running for this instance of the server!",
        )

    @patch("warnings.warn")
    @patch("subprocess.Popen")
    def test_shutdown_apache_kafka_uses_subprocess_stop_if_there_is_an_error_with_using_the_official_kafka_stop_executables(
        self, mocked_subprocess_popen: Mock, *_
    ) -> None:
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
            failing_popen_instance,
        ]

        # Start and then shut down Kafka
        startup_apache_kafka(another_app)
        shutdown_apache_kafka(another_app)

        mocked_subprocess_popen.assert_has_calls(
            [
                call(
                    apache_kafka_server_shutdown_command,
                    stderr=self.mocked_subprocess_pipe,
                    stdout=self.mocked_subprocess_pipe,
                    text=True,
                ),
            ]
        )

        first_popen_instance.terminate.assert_called_once()
        second_popen_instance.terminate.assert_called_once()

    @patch("subprocess.Popen")
    def test_shutdown_apache_kafka_raises_warning_on_erroneous_official_kafka_shutdown_executable_call(
        self, mocked_subprocess_popen
    ) -> None:
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
            failing_popen_instance,
        ]

        # Start and then shut down Kafka
        startup_apache_kafka(another_app)

        with self.assertWarns(InelegantKafkaShutdownWarning) as context:
            shutdown_apache_kafka(another_app)

        self.assertEqual(
            context.warning.__str__(),
            "Kafka's Zookeeper and Server couldn't be closed via the official Kafka closure executables! A subprocess.Popen.terminate() to their subprocesses was used instead.",
        )

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

        # first start kafka
        startup_apache_kafka(another_app)

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
        url_to_connect_to = "/ws/" + os.getenv("TEST_CHAT_UUID")

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
        with patch("api.endpoints.endpoints.Controller"):
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
    def test_endpoint_creates_new_application_controller_for_chat_session(
        self, *_
    ) -> None:
        """
        Test that endpoint creates application controller.
        :return: None
        """
        with patch("api.endpoints.endpoints.Controller") as mock_application_controller:
            with patch("controller.controller_def.websockets"):
                response = self.client.post(
                    "/set_up_chat/",
                    json={"chat_context": "Hello world"},
                    follow_redirects=True,
                )
                mock_application_controller.assert_called_once_with(
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
        with patch("api.endpoints.endpoints.Controller"):
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
