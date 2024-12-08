"""
Utility functions' module.

This module contains utility functions used in other modules.
"""

import asyncio
import random
import time
import uuid
import warnings
from typing import Optional

from confluent_kafka.admin import AdminClient, NewTopic
from sqlalchemy.orm import Session

from json_defs.message import MessageJSON
from models import Chat
from user import User


class KafkaTopicAlreadyExists(Warning):
    """
    Warning to indicate that kafka topic already exists
    """

    pass


def create_message_JSON(
    content: str,
    thread_id: int,
    context_id: int,
    partition_hint: int,
    parent_message_id: int,
) -> MessageJSON:
    """
    This function returns the MessageJSON object equivalent of the supplied arguments.

    :param content:
    :param thread_id:
    :param context_id:
    :param partition_hint:
    :param parent_message_id:
    :return: MessageJSON object (basically a python dictionary)
    """
    return MessageJSON(
        **{
            "content": content,
            "thread_id": thread_id,
            "context_id": context_id,
            "partition_hint": partition_hint,
            "parent_message_id": parent_message_id,
        }
    )


def generate_message_from_user(
    user: User,
    thread_id: int,
    context_id: int,
    partition_hint: int,
    parent_message_id: Optional[int] = None,
) -> MessageJSON:
    """
    Given user object, generate and return message from user.

    :param user: Instantiated user object
    :param thread_id: Thread ID
    :param context_id: Context ID
    :param partition_hint: Partition Hint
    :param parent_message_id: Parent Message ID (optional)
    :return: MessageJSON of the generated message.
    """
    assert isinstance(user, User)

    return create_message_JSON(
        thread_id=thread_id,
        context_id=(
            context_id
            if parent_message_id is not None
            else random.choice(
                list(
                    {
                        i for i in range(0, 1000)
                    }.difference(  # TODO: Refactor new context_id generation
                        {context_id}
                    )
                )
            )
        ),
        partition_hint=partition_hint,
        parent_message_id=parent_message_id,
        content=asyncio.run(
            user.generate_message("")
        ),  # TODO: Add prompt for querying of LLM
    )


def add_new_chat(session: Session, chat_title: str, chat_context: str) -> str:
    """
    Add new chat to database.

    :param session: Application session object
    :param chat_title: Chat title
    :param chat_context: Chat context
    :return: Added Chat uuid string to the database.
    """

    assert len(chat_title.strip()) > 0
    assert len(chat_context.strip()) > 0

    new_chat = Chat()

    new_chat.chat_title, new_chat.chat_context = chat_title, chat_context

    session.add(new_chat)
    session.flush()

    new_chat_uuid = new_chat.uuid.__str__()

    session.commit()
    return new_chat_uuid


def create_apache_kafka_topic(topic_title: str) -> None:
    """
    Function for creating Apache Kafka Topic.

    In the event where :topic_title already exists as a kafka topic, the resolution
    strategy is thus:
    - Raise a KafkaTopicAlreadyExists warning about the duplicate topic creation issue
    - Employ uuid.uuid4() to create a UUID suffix that is appended to topic_title to form a new topic string.
    - Call create_apache_kafka_topic() with the new topic string.

    :param topic_title: Title of the Apache Kafka topic intended to be created
    :return: None
    """
    try:
        assert type(topic_title) is str and len(topic_title.strip()) > 0
    except AssertionError:
        raise ValueError(
            "create_apache_kafka_topic() 'topic_title' argument must be non-empty string!"
        )
    if len(topic_title.split(" ")) != 1:
        raise ValueError(
            "create_apache_kafka_topic() 'topic_title' argument cannot contain spaces!"
        )

    a = AdminClient(
        {
            "bootstrap.servers": "localhost:9092",
        }
    )

    existing_topics = set(a.list_topics().topics.keys())
    if topic_title not in existing_topics:
        new_topic = NewTopic(topic_title, num_partitions=3, replication_factor=1)
        execution = a.create_topics([new_topic])

        # NOTE: sleep required to wait so python garbage collector doesn't clean up broker resources!
        time.sleep(1)
        if isinstance(execution[topic_title], BaseException):
            raise RuntimeError(
                f"Exception raised while creating kafka topic!: \n\n{execution[topic_title]}"
            )
    else:
        new_topic_suffix = uuid.uuid4()
        while (
            new_topic := topic_title
            + "_"
            + new_topic_suffix.__str__().replace("-", "_")
        ) in existing_topics:
            new_topic_suffix = uuid.uuid4()

        warnings.warn(
            f'Kafka topic: "{topic_title}" already exists, thus topic has been augmented to: {new_topic}',
            KafkaTopicAlreadyExists,
        )

        return create_apache_kafka_topic(new_topic)
