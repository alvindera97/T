# Telegram Event Chat Bot

## Introduction

The Telegram Event Chat Bot is designed to simulate human conversation within a Telegram group chat during an event. This software aims to enhance understanding of human communication, coordination, and perception in social event contexts by generating and managing intelligent conversations around a specified event.

## Purpose

The primary goal of this bot is to facilitate realistic interaction among participants in a Telegram group during an event, thereby offering insights into human communication dynamics. It is particularly useful for social event planning, behavioral studies, and software engineering teams looking to beta test interactive communication systems.

## Scope

This project is intended for software engineers and beta testers within the confines of controlled group chats. It does not include telemetry and focuses solely on the simulation of group conversations.

## Features

- **Event-based conversation simulation:** Messages and responses center around the event.
- **Message broadcasting:** Users can send event-related messages to the group.
- **Intelligent responses:** The bot generates contextually relevant replies.
- **Off-topic message limitation:** The percentage of messages that are off-topic are configurable.
- **AI-generated content:** Automated creation of messages and responses.

## System Architecture

The system employs an asynchronous publisher-subscriber design pattern:

- **Publisher:** A user who sends messages to the group.
- **Subscriber:** A user who responds to messages sent by publishers.

## User Roles

- [**Publisher (pub):**](https://github.com/alvindera97/PubSub-Telegram-Bot-Comments/blob/dev/design/docs/Publisher.md#publisher) Sends messages to the group.
- **Subscriber (sub):** Responds to messages sent by publishers.

## Functional Requirements

- Simulate human interaction around a specific event in a group chat.
- Manage publisher-subscriber interactions effectively.

## Non-functional Requirements

- **Security:** Managed by the frameworks and hosting platforms.
- **Performance:** Fault tolerance to ensure consistent message streams.
- **Execution:** Available on Telegram groups, initiated via hosting platform terminals.

## System Design

The system design includes sequence and use case diagrams, as well as class diagrams, outlining the flow of messages and interactions between users.

### Key Components

- **Message Store:** Holds messages sent by users.
- **Message Broker:** Manages the distribution of messages.
- **Message Composer:** Generates and formats messages.
- **Content Enricher:** Adds relevant context to messages.
- **Content Filter:** Ensures messages meet specified criteria.
- **Message Normalizer:** Standardizes message formats.
- **Recipient Poll:** Determines which users receive messages.
- **Message Dispatcher:** Sends messages to the appropriate recipients.
- **Smart Proxy:** Manages interactions with the Telegram API.

## Data Design

The system involves three primary entities:

1. **Message Object:** Based on the default Telegram Message object.
2. **Message Stream:** Managed by Apache Kafka, categorizing messages for processing.
3. **User Object:** Defined by Telegram, representing users in the group.

## Programming Languages and Frameworks

- **Languages:** Python
- **Frameworks:**
  - Telethon (for Telegram API interactions)
  - Apache Kafka (for message streaming)
  - Sphinx (for documentation)

## External Libraries and APIs

- **Telegram API:** For messaging features.
- **Apache Kafka Streams API:** For building stream processing apps.
- **OpenAI API | Gemini API:** For AI-generated content.

## Testing and Quality Assurance

- **Test Plan:** Test Driven Development (TDD) approach.
- **Automated Testing:** Utilizing unittest and GitHub Actions for CI/CD.
- **User Acceptance Testing:** Involving beta testers for real-life scenario testing.
- **Version Control:** Managed with Git, following Semantic Versioning.

## Deployment and Maintenance

### Deployment Plan

1. Automated testing on push.
2. If tests pass, publish the latest commit on the hosting platform.

### Maintenance Plan

- **Bug fixes and updates:** Triggered by dependency updates and user feedback.
- **Versioning:** Semantic versioning to indicate the nature of changes.

## Future Enhancements

- Decoupling systems for more complex functionalities.
- Smarter multimedia generation.
- Web scraping for additional content enrichment.

## Conclusion

This readme outlines the creation of a Telegram bot that simulates human conversations during events. It leverages Python, Telethon, and Apache Kafka to provide a robust solution for studying and enhancing group communication dynamics.

## References

- [Wikipedia: Publish–subscribe pattern](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern)
