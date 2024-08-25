"""
Utility functions' module.

This module contains utility functions used in other modules.
"""
import asyncio
import random
from typing import Optional

from message import MessageJSON
from user import User


def create_message_JSON(content: str, thread_id: int, context_id: int, partition_hint: int,
                        parent_message_id: int) -> MessageJSON:
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
            "parent_message_id": parent_message_id
        })


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
        context_id=context_id if parent_message_id else random.choice(
            list(
                {i for i in range(0, 1000)}.  # TODO: Refactor new context_id generation
                difference({context_id})
            )
        ),
        partition_hint=partition_hint,
        parent_message_id=parent_message_id,
        content=asyncio.run(user.generate_message(""))
    )
