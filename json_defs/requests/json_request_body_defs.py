"""
Json request body module.

This module contains class definitions for
entities representing json request body content at api endpoints.
"""

import pydantic


class SetUpChatRequestBody(pydantic.BaseModel):
    """
    Class definition for new chat request body contents.
    """

    chat_title: str
    chat_context: str
    chat_number_of_users: int
