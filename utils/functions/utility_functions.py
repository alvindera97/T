"""
Utility functions' module.

This module contains utility functions used in other modules.
"""
from message import MessageJSON


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
