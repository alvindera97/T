### Objective
Each message can either start a new context bubble or continue an existing one. The system should allows consumers (primarily consume context via an LLM) to access the full context of a message thread and some non-empty context from the entire group chat to generate appropriate responses.

### System Components
1. **Kafka Topics**: Each user has a dedicated topic, thus their messages will be found in the user's topic.
2. **Partitions**: Each user topic has a fixed number of partitions.
3. **Message Metadata**: Each message includes metadata to manage context bubbles and threads.
4. **Producers**: Send messages to Kafka topics with appropriate metadata.
5. **Subscriber**: Subscribers to and consumes messages from Kafka topics and manage context based on metadata. Consumers also respond to messages from Kafka topics via a system called "**Consumer Response**". A **Consumer Response** is simply a compound name for referring to a range of responses to a message. These include but are not limited to:
   - Sending a direct rely to a message from a pool of messages it's consuming from.
   - Quoting a message from a pool of messages it's currently consuming from.
   - Emoji-reacting to a message from a pool of messages it's currently consuming from.
   - Mentioning the username of a user that previously sent a message from a pool of messages it's currently consuming from.

### Design Details

#### 1. Kafka Topics
- **User Topics**: Each user will have a topic named `user_{user_id}`.
  - Example: `user_12345`
- **Fixed Partitions**: Each user topic will have a predefined number of partitions.
  - Example: 10 partitions per user topic

#### 2. Message Metadata
Each message includes:
- `context_id`: Unique identifier for the context bubble. New messages get a new `context_id`. Replies inherit the `context_id` of the referenced message.
- `parent_message_id`: Identifier of the message being referenced or replied to.
- `thread_id`: Identifier that groups related context bubbles. It can be the same as `context_id` for the first message in a thread.
- `partition_hint`: Used to determine which partition to send the message to. It ensures messages in the same context bubble are directed to the same partition.

#### 3. Producers (AKA Publishers)
Producers send messages to user topics with the appropriate metadata. They also determine the `partition_hint` to ensure related messages are grouped in the same partition.

**Producer Example:**

```python
from kafka import KafkaProducer
import json
import uuid
import random

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def send_message(user_id, content, context_id=None, parent_message_id=None):
    topic = f"user_{user_id}"
    partition_count = 10  # Assume 10 partitions for each user topic

    if context_id is None:
        context_id = str(uuid.uuid4())  # New context bubble
        partition_hint = random.randint(0, partition_count - 1)  # New context assigned randomly
    else:
        partition_hint = hash(context_id) % partition_count  # Same context goes to the same partition

    thread_id = parent_message_id if parent_message_id else context_id

    message = {
        "content": content,
        "context_id": context_id,
        "parent_message_id": parent_message_id,
        "thread_id": thread_id,
        "partition_hint": partition_hint
    }

    producer.send(topic, value=message, partition=partition_hint)
    print(f"Sent message to {topic} partition {partition_hint}: {message}")

# Example: Send a new message
send_message("user123", "This is a new message")

# Example: Send a reply to an existing message
send_message("user123", "This is a reply", context_id="existing_context_id", parent_message_id="existing_message_id")
```

#### 4. Consumers (AKA Subscribers)
Consumers subscribe to user topics and process messages based on their metadata. They will manage context bubbles and threads dynamically.

**Consumer Example:**

```python
from kafka import KafkaConsumer
import json

def consume_messages(user_id):
    topic = f"user_{user_id}"
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest'
    )

    for message in consumer:
        partition = message.partition
        value = message.value
        print(f"Received message from partition {partition}: {value}")

        # Process message based on its context_id and thread_id
        process_message(value)

def process_message(message):
    context_id = message['context_id']
    thread_id = message['thread_id']
    # Add logic to handle context bubbles and threads

# Example: Start consuming messages
consume_messages("user123")
```

### Considerations
- **Partition Limits**: Kafka's partition limits.
- **Context Management Logic**: Implementation of robust logic to manage context bubbles and threads dynamically is no small task and  I can imagine that each individual will have opinionated approaches to this, in the future of this project, it would be a nice-to-have to allow people implement their context management logic (probably via an [interface](https://en.wikipedia.org/wiki/Interface_(object-oriented_programming))).
