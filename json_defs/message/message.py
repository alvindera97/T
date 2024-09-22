"""
Message module.

This module contains class and related object/attribute definitions for application message structure.
"""

from typing import Optional

import pydantic


class MessageJSON(pydantic.BaseModel):
    """
    TypedDict-like definition of JSON object schema for generated message
    """

    content: str
    thread_id: int
    context_id: int
    partition_hint: int
    parent_message_id: Optional[int]
