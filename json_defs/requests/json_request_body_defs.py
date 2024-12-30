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


class GetChatInfoRequestBody(pydantic.BaseModel):
    """
    Class definition for request body for retrieving chat information.
    """

    chat_uuid: str
