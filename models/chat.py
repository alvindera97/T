"""
Message model module.

This module contains class and module definitions for the Message model
"""

import uuid

from sqlalchemy import Column, UUID, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chat(Base):
    """
    Message model class.
    """

    __tablename__ = "Chats"

    chat_title = Column("chat_title", String, nullable=False)
    uuid = Column("uuid", UUID, primary_key=True, default=uuid.uuid4)
    chat_context = Column("chat_context", String, nullable=False)
    chat_number_of_users = Column(
        "chat_number_of_users", Integer, nullable=False, default=1
    )
