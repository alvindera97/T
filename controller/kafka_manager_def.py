"""
Kafka Manager module (also referable to as 'Application Controller Kafka Manager' module)

This module contains the class and module definitions for the Application Controller Kafka Manager
"""

import asyncio
from typing import Tuple

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from utils import exceptions


class KafkaManager:

    def __init__(self, number_of_users: int):
        self.__consumers = tuple()
        self.__producers = tuple()

        for i in range(number_of_users):
            if i % min(10, (number_of_users // 2) + 1) == 0:
                self.__consumers += (AIOKafkaConsumer(),)
                self.__producers += (AIOKafkaProducer(),)

    @property
    def consumers(self) -> Tuple[AIOKafkaConsumer]:
        return self.__consumers

    @property
    def producers(self) -> Tuple[AIOKafkaProducer]:
        return self.__producers

    @producers.setter
    def producers(self, *args, **kwargs):
        raise exceptions.OperationNotAllowedException(
            "Modification of Kafka Manager Producers Is Not Allowed"
        )

    @consumers.setter
    def consumers(self, *args, **kwargs):
        raise exceptions.OperationNotAllowedException(
            "Modification of Kafka Manager Consumers Is Not Allowed"
        )

    @consumers.deleter
    def consumers(self, *args, **kwargs):
        raise exceptions.OperationNotAllowedException(
            "Deletion of Kafka Manager Consumers Is Not Allowed"
        )

    @producers.deleter
    def producers(self, *args, **kwargs):
        raise exceptions.OperationNotAllowedException(
            "Deletion of Kafka Manager Producers Is Not Allowed"
        )

    async def __close(self):
        """
        Gracefully close the Kafka manager.
        :return: None
        """

        for consumer in self.consumers:
            if type(consumer) is AIOKafkaConsumer:
                await consumer.stop()
        for producer in self.producers:
            if type(producer) is AIOKafkaProducer:
                await producer.stop()

    def __del__(self):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.__close())
        except RuntimeError:
            asyncio.run(self.__close())


class KafkaManagerFactory:
    """
    Class definition for the kafka manager employed primarily by the application controller.
    """

    @staticmethod
    def create_base_kafka_manager(number_of_users: int = None) -> KafkaManager:
        """
        Create and return bare-minimum Kafka Manager object.
        :param number_of_users: Number of users participating in chat.
        :return: KafkaManager object.
        """
        if number_of_users is None:
            raise ValueError(
                "You must supply the number of users the kafka manager is catering for!"
            )

        if type(number_of_users) is not int or (
            type(number_of_users) is int and number_of_users < 1
        ):
            raise ValueError(
                "You must supply a non-zero positive integer for number of users the kafka manager is catering for!"
            )

        return KafkaManager(number_of_users)
