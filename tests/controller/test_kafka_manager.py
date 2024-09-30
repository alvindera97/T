"""
Module for tests on application controller Kafka Manager.

This module contains test cases or testing the "Controller's Kafka Manager" (otherwise called Application Controller
Kafka Manager) entity and all related functionality.
"""

import inspect
import random
import unittest
from unittest.mock import patch, AsyncMock

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

import controller
from controller import KafkaManagerFactory
from utils.exceptions import OperationNotAllowedException


# KafkaManagerFactory -> KafkaManager
# KafkaManager


class TestKafkaManagerFactory(unittest.IsolatedAsyncioTestCase):
    """
    Test class for tests on application controller kafka manager factory class
    """

    def test_kafka_manager_factory_class_exists(self) -> None:
        """
        Test that the class for controller kafka manager factory exists.
        :return: None
        """

        self.assertTrue(inspect.isclass(controller.KafkaManagerFactory))

    async def test_kafka_manager_factory_method_for_creating_base_kafka_manager_works(
        self,
    ) -> None:
        """
        Test that the class for controller kafka manager has method that returns kafka manger.
        :return: None
        """
        self.assertTrue(
            isinstance(
                controller.KafkaManagerFactory.create_base_kafka_manager(1),
                controller.KafkaManager,
            )
        )

    def test_kafka_manager_factory_method_for_creating_base_kafka_manager_takes_a_non_zero_input_for_number_of_users(
        self,
    ) -> None:
        """
        Test that the method for creating base kafka manager within the kafka manager factory takes number of chat users.
        :return: None
        """

        with self.assertRaises(ValueError) as context_1:
            controller.KafkaManagerFactory.create_base_kafka_manager()

        with self.assertRaises(ValueError) as context_2:
            controller.KafkaManagerFactory.create_base_kafka_manager(
                random.choice(
                    [
                        "1",
                        True,
                        False,
                        1.1,
                        (1,),
                        [
                            1,
                        ],
                    ]
                )
            )

        with self.assertRaises(ValueError) as context_3:
            controller.KafkaManagerFactory.create_base_kafka_manager(
                random.choice([0, -1])
            )

        self.assertEqual(
            context_1.exception.__str__(),
            "You must supply the number of users the kafka manager is catering for!",
        )

        self.assertEqual(
            context_2.exception.__str__(),
            "You must supply a non-zero positive integer for number of users the kafka manager is catering for!",
        )

        self.assertEqual(
            context_3.exception.__str__(),
            "You must supply a non-zero positive integer for number of users the kafka manager is catering for!",
        )


class TestKafkaManager(unittest.IsolatedAsyncioTestCase):
    """
    Test class for tests on application controller kafka manager
    """

    def test_kafka_manager_class_exists(self) -> None:
        """
        Test that the class for controller kafka manager exists.
        :return: None
        """

        self.assertTrue(inspect.isclass(controller.KafkaManager))

    def test_instantiated_kafka_manager_class_has_consumers_property(self) -> None:
        """
        Test that instantiated kafka manager class has consumers property
        :return: None
        """
        self.assertTrue(controller.KafkaManager.consumers, property)

    async def test_instantiated_kafka_manager_class_consumers_property_is_immutable(
        self,
    ) -> None:
        """
        Test that instantiated kafka manager class consumers property is immutable

        :return: None
        """
        kafka_manager = KafkaManagerFactory.create_base_kafka_manager(1)

        with self.assertRaises(OperationNotAllowedException) as context_1:
            del kafka_manager.consumers

        with self.assertRaises(OperationNotAllowedException) as context_2:
            kafka_manager.consumers = [object]

        self.assertEqual(
            context_1.exception.__str__(),
            "Deletion of Kafka Manager Consumers Is Not Allowed",
        )
        self.assertEqual(
            context_2.exception.__str__(),
            "Modification of Kafka Manager Consumers Is Not Allowed",
        )

    def test_instantiated_kafka_manager_class_has_producers_property(self) -> None:
        """
        Test that instantiated kafka manager class has producers property

        :return: None
        """
        self.assertTrue(controller.KafkaManager.producers, property)

    async def test_instantiated_kafka_manager_class_producers_property_is_immutable(
        self,
    ) -> None:
        """
        Test that instantiated kafka manager class producers property is immutable

        :return: None
        """

        kafka_manager = KafkaManagerFactory.create_base_kafka_manager(1)

        with self.assertRaises(OperationNotAllowedException) as context_1:
            del kafka_manager.producers

        with self.assertRaises(OperationNotAllowedException) as context_2:
            kafka_manager.producers = [object]

        self.assertEqual(
            context_1.exception.__str__(),
            "Deletion of Kafka Manager Producers Is Not Allowed",
        )
        self.assertEqual(
            context_2.exception.__str__(),
            "Modification of Kafka Manager Producers Is Not Allowed",
        )

    async def test_instantiated_kafka_manager_class_producers_property_returns_a_tuple_of_AIOKafkaProducers_objects(
        self,
    ) -> None:
        """
        Test that instantiated kafka manager class producers property returns a tuple of AIOKafkaProducer objects.

        :return: None
        """

        with patch(
            "controller.kafka_manager_def.AIOKafkaConsumer", spec=AIOKafkaConsumer
        ):
            with patch(
                "controller.kafka_manager_def.AIOKafkaProducer", spec=AIOKafkaProducer
            ):
                kafka_manger = KafkaManagerFactory.create_base_kafka_manager(10)

                self.assertTrue(type(kafka_manger.producers) is tuple)
                self.assertTrue(
                    len(kafka_manger.producers) > 0,
                    "KafkaManager doesn't have any producers to run this test with!",
                )

                for producer in kafka_manger.producers:
                    self.assertTrue(
                        isinstance(producer, AIOKafkaProducer),
                        f"producer: {producer} is not an instance of AIOKafkaProducer but of {type(producer)}",
                    )

    async def test_instantiated_kafka_manager_class_consumers_property_returns_a_tuple_of_AIOKafkaConsumers_objects(
        self,
    ) -> None:
        """
        Test that instantiated kafka manager class consumers property returns a tuple of AIOKafkaConsumer objects.

        :return: None
        """
        with patch(
            "controller.kafka_manager_def.AIOKafkaConsumer", spec=AIOKafkaConsumer
        ):
            with patch(
                "controller.kafka_manager_def.AIOKafkaProducer", spec=AIOKafkaProducer
            ):

                kafka_manger = KafkaManagerFactory.create_base_kafka_manager(10)

                self.assertTrue(type(kafka_manger.consumers) is tuple)
                self.assertTrue(
                    len(kafka_manger.consumers) > 0,
                    "KafkaManager doesn't have any consumers to run this test with!",
                )

                for consumer in kafka_manger.consumers:
                    self.assertTrue(
                        isinstance(
                            consumer,
                            AIOKafkaConsumer,
                        ),
                        f"consumer: {consumer} is not an instance of AIOKafkaConsumer but of {type(consumer)}",
                    )

    async def test_on_instantiation_of_kafka_manager_class_all_producer_and_consumer_instances_are_started(
        self,
    ) -> None:
        """
        Test that on instantiation of kafka manager class, all producer and consumer instances are started.
        :return: None
        """

        with patch(
            "controller.kafka_manager_def.AIOKafkaConsumer", spec=AIOKafkaConsumer
        ):
            with patch(
                "controller.kafka_manager_def.AIOKafkaProducer", spec=AIOKafkaProducer
            ):

                kafka_manager = KafkaManagerFactory.create_base_kafka_manager(10)

                for consumer, producer in zip(
                    kafka_manager.producers, kafka_manager.consumers
                ):
                    self.assertTrue(consumer._closed)
                    self.assertTrue(producer._closed)

    async def test_on_closure_of_kafka_manager_class_close_method_is_called(
        self,
    ) -> None:
        """
        Test that on closure / clean up of the kafka manager class, method to close all producer / consumer instances of the kafka
        manager is called.
        :return: None
        """

        with patch(
            "controller.kafka_manager_def.AIOKafkaConsumer", spec=AIOKafkaConsumer
        ):
            with patch(
                "controller.kafka_manager_def.AIOKafkaProducer", spec=AIOKafkaProducer
            ):
                mocked_manager_close_method_patch = patch(
                    "controller.kafka_manager_def.KafkaManager._KafkaManager__close",
                    new=AsyncMock(),
                )
                mocked_manager_close_method = mocked_manager_close_method_patch.start()

                kafka_manager = KafkaManagerFactory.create_base_kafka_manager(10)

                kafka_manager.__del__()

                mocked_manager_close_method.assert_called_once()

                mocked_manager_close_method_patch.stop()

    async def test_close_method_of_kafka_manager_class_stops_all_producers_and_producers(
        self,
    ) -> None:
        """
        Test that calling Kafka Manager close() method stops all producer / consumer instances of the kafka
        manager.

        :return: None
        """
        with patch(
            "controller.kafka_manager_def.AIOKafkaConsumer", spec=AIOKafkaConsumer
        ):
            with patch(
                "controller.kafka_manager_def.AIOKafkaProducer", spec=AIOKafkaProducer
            ):

                kafka_manager = KafkaManagerFactory.create_base_kafka_manager(100)

                await kafka_manager._KafkaManager__close()

                # We're expecting all producers and consumers to be closed

                for producer in kafka_manager.producers:
                    self.assertTrue(producer._closed)

                for consumer in kafka_manager.consumers:
                    self.assertTrue(consumer._closed)
