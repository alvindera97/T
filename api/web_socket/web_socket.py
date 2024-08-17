"""
Websocket API module.

This module contains method(s) defining application any web socket endpoint(s)
"""
import os
import uuid

from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/chat/{chat_uuid}")
async def handle_chat(websocket: WebSocket, chat_uuid: uuid.UUID):
    """
    Handle chat operations on chat with id {chat_uuid}.
    :param websocket: FastAPI Websocket object for websocket operations.
    :param chat_uuid: UUID of chat
    :return:
    """
    await websocket.accept()

    if chat_uuid != os.getenv('TEST_CHAT_URL'):
        raise Exception("Invalid chat URL")
