"""
User module (also referable to as 'Client' module)

This module contains the class and module definitions for the User (Client) entity.

Classes:
  User: Provides definitions for the User entity object and its functionalities.

"""
from telethon import TelegramClient


class User:
    """
    Class definition for the User entity
    """

    def __init__(self, api_id: int, api_hash: str) -> None:
        """
        Class initializer
        :param api_id: Telegram client API ID (issued by telegram)
        :param api_hash: Telegram client API_HASH for corresponding API_ID
        :return: None
        """

        self.telegram_client = TelegramClient("default", api_id, api_hash)
