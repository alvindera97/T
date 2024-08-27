"""
Message model module.

This module contains class and module definitions for the Message model
"""
import uuid

from sqlalchemy import (
    Column,
    UUID
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chat(Base):
    """
    Message model class.
    """

    __tablename__ = "Chats"

    uuid = Column("uuid", UUID, primary_key=True, default=uuid.uuid4)
