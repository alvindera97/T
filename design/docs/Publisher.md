# Publisher
The publisher is the primary entity responsible for sending messages to a group chat. This means that for User object to be able to send messages, they must do so as a [Kafka Publisher](https://kafka-python.readthedocs.io/en/master/#kafkaproducer). What is the implication of this design choice? 

> The implication is that every user object must be able to act as a publisher at runtime (basically instantly)

## How will the Publisher work?
Ideally, once a User object is staged to send a  message, the User object can choose to do one of 2 things:
- Interact with a message that it's currently subscribed to
- Simply send a new message.

Looking at the options in detail:
### Interact with a message that it's currently subscribed to:

NOTE: This is only a viable option if the User object is subscribed to a minimum of 1 topic in the message stream where the minimum number of events in all of the topics subscribed to is 1 

This "interaction" is a general term for reacting to a Kafka topic that has been subscribed to; let's call the message that started the topic `sub-message`. So this could range from reacting to the `sub-message` to sending a message referencing the contents of the Kafka topic, or sending a message replying to any single event (message) in that Kafka topic. The possibilities here are only partially limited by the Apache Kafka Streams API.