"""
Websocket API module.

This module contains method(s) defining application any web socket endpoint(s)
"""

import os
import uuid
import warnings
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from controller import Controller
from database import db
from json_defs.requests import json_request_body_defs as json
from utils.functions import utility_functions


class InelegantKafkaShutdownWarning(Warning):
    """
    Warning to indicate issues with shutdown of kafka
    """

    pass


class MultipleKafkaProducerStartWarning(Warning):
    """
    Warning to indicate attempt to start kafka producer on app with existing kafka producer.
    """

    pass


async def start_apache_kafka_producer(fastapi_application: FastAPI):
    """
    Starts the Apache Kafka producer

    :param fastapi_application: Instance of FastAPI application to set properties on.
    """

    if hasattr(fastapi_application.state, "kafka_producer"):
        warnings.warn(
            f"There's an existing kafka producer for this app instance: {hex(id(fastapi_application))}",
            MultipleKafkaProducerStartWarning,
        )
        return

    fastapi_application.state.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=f'{os.getenv("APACHE_KAFKA_BOOTSTRAP_SERVER_HOST")}:{os.getenv("APACHE_KAFKA_BOOTSTRAP_SERVER_PORT")}'
    )

    await fastapi_application.state.kafka_producer.start()


async def close_apache_kafka_producer(fastapi_application: FastAPI):
    """
    Closes the Apache Kafka producer

    :param fastapi_application: Instance of FastAPI application to consume properties from.
    """
    if not hasattr(fastapi_application.state, "kafka_producer"):
        warnings.warn(
            "You cannot shutdown apache kafka producer as there's none [recorded] running for this instance of the server!",
            InelegantKafkaShutdownWarning,
        )
        return
    await fastapi_application.state.kafka_producer.stop()


@asynccontextmanager
async def lifespan(fastapi_application: FastAPI):
    """
    Run start up and shut down operations for the server.

    Code before the yield statement gets called before running server, while code after
    the yield statement gets called during the closure of the server.
    :param fastapi_application: FastAPI app instance.
    """

    await start_apache_kafka_producer(fastapi_application)

    yield

    await close_apache_kafka_producer(fastapi_application)


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS", "GET", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.websocket("/chat/{chat_uuid}")
async def handle_chat(websocket: WebSocket, chat_uuid: uuid.UUID):
    """
    Handle chat operations on chat with id {chat_uuid}.
    :param websocket: FastAPI Websocket object for websocket operations.
    :param chat_uuid: UUID of chat
    :return:
    """
    await websocket.accept()

    if chat_uuid.__str__() != os.getenv("TEST_CHAT_URL"):
        raise Exception("Invalid chat URL")

    while True:
        data = await websocket.receive_text()
        print(f"message just sent now: {data.__str__()}")
        break


@app.post("/set_up_chat", response_class=RedirectResponse, status_code=302)
async def set_up_chat(
    request_json_body: json.SetUpChatRequestBody, session: Session = Depends(db.get_db)
):
    """
    Endpoint for setting up chat.

    Creates a unique chat uuid and saves in database returning a redirect response.
    :return:
    """
    new_chat_uuid = utility_functions.add_new_chat(
        session, request_json_body.chat_title, request_json_body.chat_context
    )
    chat_url = "chat/" + new_chat_uuid

    try:
        utility_functions.create_apache_kafka_topic(new_chat_uuid)
    except Exception as e:
        print(f">>> Exception while attempting to create kafka topic: \n\n{e}")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred at the final stages of setting up your new chat.",
        )

    await Controller.initialise(
        1, f"ws://localhost:8000/{chat_url}", request_json_body.chat_context
    )

    return f"{os.getenv('HOST_URL')}/{chat_url}"
