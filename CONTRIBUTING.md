_This document is the single source of truth concerning contributions to this project. It will be kept up to date as the project remains actively maintained and as we all learn from past experiences and future considerations._
# How To Contribute
Officially, you can contribute to this project via raising issues, reporting bugs and sending in pull requests!
## Raising Issues
### **Did you find a bug?**
- **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/alvindera97/T/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/alvindera97/T/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.
- Grammatical errors, outdated comments and incorrect docstrings situations are also considered bugs. 
## Pull Requests
### **Did you write a patch that fixes a bug?**
- Open a new GitHub pull request with the patch.
- Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.
- Before submitting, please read the ["Setting Up Your Machine" section](https://github.com/alvindera97/T/blob/trunk/CONTRIBUTING.md#setting-up-your-machine) and the  ["A Note On Tests" section](https://github.com/alvindera97/T/blob/trunk/CONTRIBUTING.md#a-note-on-tests) of the this contributing guide to know more about setting up your development environment, tests and coding conventions.
### **Did you correct outdated or incorrectly written documentation**?
- Open a new GitHub pull request with the correction.
- Ensure the PR description clearly describes the problem and solution. Link the relevant issue if applicable.
## Setting Up Your Machine
### Get The Source Code (the name of the main branch is `trunk`)
You can use git to clone the source code via the command:
`git clone git@github.com:alvindera97/T.git`

Then you can change directory (`cd`) into the T folder via the command: 
`cd T`
### Python Version (`3.10` or `3.10` in a virtual environment)
#### Without a virtual environment
To set up your machine consider using python version `3.10` . I am not aware of any breaking changes on versions higher than `python-3.10`, however on python version `3.10`, there are no deprecation warnings. 
#### With a virtual environment
To set up a machine consider using python version `3.10`. I am not aware of any breaking changes in versions higher than `python-3.10`, however on python `3.10`, there are no deprecation warnings. 
##### Create the virtual environment
You can follow this guide for creating virtual environments: 
https://docs.python.org/3/library/venv.html
### Development Dependencies 
#### PostgreSQL
*Install PostgreSQL:*
You can install PostgreSQL by following the instructions on this page: https://www.postgresql.org/download/
#### Python Dependencies
To install the development requirements, you'll need to use pip:
`python -m pip install -r requirements.txt`
#### Apache Kafka 
*Install Apache Kafka (**You'll also need Java installed to run Apache Kafka**):*
You can follow the Apache Kafka installation page: https://kafka.apache.org/downloads
#### Google Gemini API Key
You can get your Google Gemini API Key by following the instructions on this page: https://ai.google.dev/gemini-api/docs/api-key
#### Environment Variables (CRITICALLY IMPORTANT)
**Using a .env file:**
If you're going to use a .env file to store all these environment variables, you'll need to install `python-dotenv`: 
`pip install python-dotenv`

You will need to set up the following environment variables:
`GOOGLE_API_KEY` (API Key for Google Gemini AI)
`TEST_CHAT_UUID` (e.g. chat/342498g2-87x3-4a64-9325-rb70471623ax)
`DATABASE_URL` (postgresql database URL)
`APACHE_KAFKA_OPS_MAX_WAIT_TIME_SECS` ((integer) number of seconds to wait for kafka zookeeper & kafka server start e.g. 5)
`APACHE_KAFKA_ZOOKEEPER_SERVER_START_EXECUTABLE_FULL_PATH` (/path/to/zookeeper-server-start.sh)
`APACHE_KAFKA_ZOOKEEPER_KAFKA_ZOOKEEPER_PROPERTIES_FULL_PATH` (/path/to/zookeeper.properties)
`APACHE_KAFKA_ZOOKEEPER_SERVER_STOP_EXECUTABLE_FULL_PATH` (/path/to/zookeeper-server-stop.sh)
`APACHE_KAFKA_SERVER_PROPERTIES_FULL_PATH` (/path/to/server.properties)
`APACHE_KAFKA_SERVER_START_EXECUTABLE_FULL_PATH` (/path/to/kafka-server-start.sh)
`APACHE_KAFKA_SERVER_STOP_EXECUTABLE_FULL_PATH` (/path/to/kafka-server-stop.sh)
`APACHE_KAFKA_CONSUMER_EXECUTABLE_FULL_PATH` (/path/to/kafka-console-consumer.sh)
`APACHE_KAFKA_CONSUMER_PROPERTIES_FULL_PATH` (/path/to/consumer.properties)
`APACHE_KAFKA_BOOTSTRAP_SERVER_HOST` (e.g. "localhost")
`APACHE_KAFKA_BOOTSTRAP_SERVER_PORT` (e.g. "9092")

## A Note On Tests
All pull requests that include new functionality will require corresponding tests. All pull requests including functionality modification will include new tests or test modification(s) especially if your code modifications cause existing tests to fail.

## Running Tests
### Running tests with the required environment variables in .env file:
To run test, you'll need to use the command: 
`dotenv -- run python -m unittest`

### Running test without the required environment variables in a .env file
Note that these environment variables covered [here](https://github.com/alvindera97/T/blob/trunk/CONTRIBUTING.md#environment-variables-critically-important).

To run tests, you'll need to use the command:
`python -m unittest`

## Running The Application
### Running the application with the required environment variables in a .env file:
`dotenv -- fastapi dev api/endpoints/endpoints.py`

### Running the application without the required environment variables in a .env file:
`fastapi dev api/endpoints/endpoints.py`