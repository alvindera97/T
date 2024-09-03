"""
Websocket API module.

This module contains method(s) defining application any web socket endpoint(s)
"""
import os
import uuid
from concurrent.futures.thread import ThreadPoolExecutor

from fastapi import FastAPI, WebSocket
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from controller import Controller
from database import db
from json_defs.requests import json_request_body_defs as json
from utils.functions import utility_functions

app = FastAPI()
executor = ThreadPoolExecutor()


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


@app.post("/set_up_chat", response_class=RedirectResponse, status_code=302)
async def set_up_chat(request_json_body: json.SetUpChatRequestBody, session: Session = Depends(db.get_db)):
    """
    Endpoint for setting up chat.

    Creates a unique chat uuid and saves in database returning a redirect response.
    :return:
    """
    chat_url = "chat/" + utility_functions.add_new_chat(session)

    # run blocking Controller function in separate thread.
    executor.submit(Controller, 1, 'ws://localhost:8000/' + chat_url)

    return chat_url
