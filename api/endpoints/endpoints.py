"""
Websocket API module.

This module contains method(s) defining application any web socket endpoint(s)
"""
import os
import uuid

from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.orm import Session

from database import db
from utils.functions import utility_functions

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

    if chat_uuid.__str__() != os.getenv('TEST_CHAT_UUID'):
        raise Exception("Invalid chat URL")

    while True:
        data = await websocket.receive_text()
        print(f'message just sent now: {data.__str__()}')
        break


@app.post("/set_up_chat")
async def set_up_chat(db_session: Session = Depends(db.get_db)):
    """
    Endpoint for setting up chat.

    Creates a unique chat uuid and saves in database returning a redirect response.
    :return:
    """
    utility_functions.add_new_chat(db_session)

    # TODO: Add redirect to chat
