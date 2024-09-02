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
    chat_context: str
