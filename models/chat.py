"""
Message model module.

This module contains class and module definitions for the Message model
"""

from sqlalchemy import (
    Column,
    Integer,
    UUID
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chat(Base):
    """
    Message model class.
    """

    __tablename__ = "Chats"

    uuid = UUID()
    id = Column("id", Integer, primary_key=True)
