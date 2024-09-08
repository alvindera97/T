"""
Websocket API module.

This module contains method(s) defining application any web socket endpoint(s)
"""
import asyncio
import os
import subprocess
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from controller import Controller
from database import db
from json_defs.requests import json_request_body_defs as json
from utils.functions import utility_functions


async def start_apache_kafka_consumer():
    """
    Starts the Apache Kafka consumer
    """
    pass


async def start_apache_kafka_producer():
    """
    Starts the Apache Kafka producer
    """
    pass


async def close_apache_kafka_producer():
    """
    Closes the Apache Kafka producer
    """
    pass


async def close_apache_kafka_consumer():
    """
    Closes the Apache Kafka consumer
    """
    pass


def startup_apache_kafka(fastapi_application: FastAPI):
    """
    Starts Apache Kafka

    It essentially does 2 things:
    1. Starts zookeeper
    2. Starts the apache kafka server.

    :param fastapi_application: Instance of FastAPI application to set properties on.
    """

    # Start Apache Kafka Zookeeper
    apache_kafka_zookeeper_startup_command = [
        os.getenv("APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH"),
        os.getenv("ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH")
    ]

    process = subprocess.Popen(
        apache_kafka_zookeeper_startup_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    if process.returncode is not None:  # We're not expecting zookeeper to stop and return a returncode.
        raise subprocess.CalledProcessError(
            returncode=process.returncode,
            cmd=apache_kafka_zookeeper_startup_command,
        )

    fastapi_application.state.zookeeper_subprocess = process


def shutdown_apache_kafka():
    """
    Shutdown Apache Kafka
    """
    pass


@asynccontextmanager
async def lifespan(fastapi_application: FastAPI):
    """
    Run start up and shut down operations for the server.

    Code before the yield statement gets called before running server, while code after
    the yield statement gets called during the closure of the server.
    :param fastapi_application: FastAPI app instance.
    """

    startup_apache_kafka(fastapi_application)

    fastapi_application.state.consumer_task = await start_apache_kafka_consumer()
    fastapi_application.state.producer_task = await start_apache_kafka_producer()

    yield

    await asyncio.gather(close_apache_kafka_producer(), close_apache_kafka_consumer())

    shutdown_apache_kafka()


app = FastAPI(lifespan=lifespan)
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
    executor.submit(Controller, 1, 'ws://localhost:8000/' + chat_url, request_json_body.chat_context)

    return chat_url
