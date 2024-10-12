"""
Utility functions' module.

This module contains utility functions used in other modules.
"""

import asyncio
import os
import random
import select
import subprocess
from typing import Optional

import eventlet
from fastapi import FastAPI
from sqlalchemy.orm import Session

from json_defs.message import MessageJSON
from models import Chat
from user import User


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


def add_new_chat(session: Session) -> str:
    """
    Add new chat to database.
    :return: Added Chat uuid string to the database
    """

    new_chat = Chat()
    session.add(new_chat)
    session.flush()

    new_chat_uuid = new_chat.uuid.__str__()

    session.commit()
    return new_chat_uuid


def create_apache_kafka_topic(topic_title: str) -> None:
    """
    Function for creating Apache Kafka Topic
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

    try:
        assert isinstance(fastapi_application, FastAPI)
    except AssertionError:
        raise ValueError(
            "create_apache_kafka_topic() 'fastapi_application' must be a FastAPI instance!"
        )

    if not hasattr(fastapi_application.state, "zookeeper_subprocess"):
        raise RuntimeError(
            "fastapi_application instance has no running Apache Kafka Zookeeper server"
        )

    CREATE_KAFKA_TOPIC_COMMAND = [
        os.getenv("APACHE_KAFKA_TOPICS_EXECUTABLE_FULL_PATH"),
        "--create",
        "--bootstrap-server",
        f"{os.getenv('APACHE_KAFKA_BOOTSTRAP_SERVER_HOST')}:{os.getenv('APACHE_KAFKA_BOOTSTRAP_SERVER_PORT')}",
        "--topic",
        topic_title,
    ]

    wait_time = int(os.getenv("APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS"))
    create_kafka_topic_subprocess = subprocess.Popen(
        CREATE_KAFKA_TOPIC_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    try:
        while eventlet.Timeout(wait_time):
            reads = [
                create_kafka_topic_subprocess.stdout,
                create_kafka_topic_subprocess.stderr,
            ]
            ready_to_read, _, _ = select.select(reads, [], [], 0.1)

            for pipe in ready_to_read:
                output = pipe.readline()

                if output:
                    if f"Created topic {topic_title}." in output.strip():
                        return
    except eventlet.timeout.Timeout:
        raise RuntimeError(
            f"Failed to create kafka topic within {wait_time} second{'' if wait_time == 1 else 's'}. To increase this wait time, increase APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS env."
        )
